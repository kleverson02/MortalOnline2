#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def debug_positions():
    mem = Reader("GameThread")
    uworld = mem.read(offsets.GWorld, "Q")
    persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
    actor_array, actor_count = mem.read(persistent_level + offsets.ActorArray, "QI")
    
    print(f"ActorCount: {actor_count}")
    
    # Obter o jogador local para referência
    game_instance = mem.read(uworld + offsets.OwningGameInstance, "Q")
    local_players = mem.read(game_instance + offsets.LocalPlayers, "Q")
    local_player = mem.read(local_players, "Q")
    controller = mem.read(local_player + offsets.PlayerController, "Q")
    local_pawn = mem.read(controller + offsets.AcknowledgedPawn, "Q")
    
    print(f"Local Pawn: 0x{local_pawn:X}")
    
    # Testar diferentes offsets para RootComponent e RootPos
    root_offsets = [0x1A0, 0x1A8, 0x1B0, 0x1B8, 0x1C0]
    pos_offsets = [0xE0, 0xE8, 0xF0, 0xF8, 0x100, 0x108, 0x110, 0x118, 0x120, 0x128, 0x130]
    
    # Primeiro, encontrar a posição do jogador local para referência
    local_pos = None
    if local_pawn:
        for root_offset in root_offsets:
            root_comp = mem.read(local_pawn + root_offset, "Q")
            if not root_comp or root_comp < 0x10000000:
                continue
                
            for pos_offset in pos_offsets:
                try:
                    pos = mem.read(root_comp + pos_offset, "3d")
                    if all(-1000000 < p < 1000000 for p in pos) and any(p != 0 for p in pos):
                        print(f"Possível posição do jogador local: {pos}")
                        print(f"RootComponent: 0x{root_offset:X}, RootPos: 0x{pos_offset:X}")
                        local_pos = pos
                        return root_offset, pos_offset
                except:
                    continue
    
    return None, None

if __name__ == "__main__":
    root_offset, pos_offset = debug_positions()
    
    if root_offset and pos_offset:
        print(f"\nOffsets encontrados:")
        print(f"RootComponent = 0x{root_offset:X}")
        print(f"RootPos = 0x{pos_offset:X}")
        
        update = input("Atualizar offsets.py? (s/n): ").lower() == 's'
        if update:
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            
            content = content.replace(
                f"RootComponent = 0x{offsets.RootComponent:X}",
                f"RootComponent = 0x{root_offset:X}"
            )
            content = content.replace(
                f"RootPos = 0x{offsets.RootPos:X}",
                f"RootPos = 0x{pos_offset:X}"
            )
            
            with open("lib/offsets.py", "w") as f:
                f.write(content)
            print("Arquivo offsets.py atualizado!")