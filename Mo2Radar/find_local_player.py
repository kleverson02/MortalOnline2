#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def find_local_player():
    """Encontra o jogador local e suas informações"""
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
    
    # Obter o jogador local
    game_instance = mem.read(uworld + offsets.OwningGameInstance, "Q")
    local_players = mem.read(game_instance + offsets.LocalPlayers, "Q")
    local_player = mem.read(local_players, "Q")
    controller = mem.read(local_player + offsets.PlayerController, "Q")
    local_pawn = mem.read(controller + offsets.AcknowledgedPawn, "Q")
    
    print(f"UWorld: 0x{uworld:X}")
    print(f"PersistentLevel: 0x{persistent_level:X}")
    print(f"GameInstance: 0x{game_instance:X}")
    print(f"LocalPlayers: 0x{local_players:X}")
    print(f"LocalPlayer: 0x{local_player:X}")
    print(f"Controller: 0x{controller:X}")
    print(f"Local Pawn: 0x{local_pawn:X}")
    
    if not local_pawn or local_pawn < 0x10000000:
        print("Jogador local não encontrado ou inválido.")
        return None
    
    # Obter o nome do jogador local
    try:
        name_addr, name_length = mem.read(local_pawn + offsets.CreatureName, "QB")
        if name_addr > 0x10000000 and 0 < name_length < 50:
            name_bytes = max(0, name_length * 2 - 2)
            name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
            print(f"Nome do jogador local: {name}")
    except:
        print("Não foi possível ler o nome do jogador local.")
    
    # Testar diferentes offsets para RootComponent
    print("\nTestando diferentes offsets para RootComponent:")
    for rc_offset in [0x188, 0x190, 0x198, 0x1A0, 0x1A8, 0x1B0, 0x1B8]:
        try:
            root_component = mem.read(local_pawn + rc_offset, "Q")
            if root_component and root_component > 0x10000000:
                print(f"\nRootComponent em 0x{rc_offset:X}: 0x{root_component:X}")
                
                # Testar diferentes offsets para RootPos
                for pos_offset in [0xE0, 0xE8, 0xF0, 0xF8, 0x100, 0x108, 0x110]:
                    try:
                        # Tentar ler como float32
                        pos = mem.read(root_component + pos_offset, "3f")
                        if all(-1000000 < p < 1000000 for p in pos):
                            print(f"  Posição em 0x{pos_offset:X} (float32): {pos}")
                    except:
                        pass
                    
                    try:
                        # Tentar ler como float64
                        pos = mem.read(root_component + pos_offset, "3d")
                        if all(-1000000 < p < 1000000 for p in pos):
                            print(f"  Posição em 0x{pos_offset:X} (float64): {pos}")
                    except:
                        pass
        except:
            pass
    
    # Perguntar se deseja atualizar os offsets
    print("\nDigite os novos offsets (deixe em branco para manter o atual):")
    
    new_rc = input(f"RootComponent (atual: 0x{offsets.RootComponent:X}): ")
    if new_rc:
        try:
            rc_value = int(new_rc, 16)
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            content = content.replace(
                f"RootComponent = 0x{offsets.RootComponent:X}",
                f"RootComponent = 0x{rc_value:X}"
            )
            with open("lib/offsets.py", "w") as f:
                f.write(content)
            print(f"RootComponent atualizado para 0x{rc_value:X}")
        except:
            print("Valor inválido. Nenhuma alteração foi feita.")
    
    new_rp = input(f"RootPos (atual: 0x{offsets.RootPos:X}): ")
    if new_rp:
        try:
            rp_value = int(new_rp, 16)
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            content = content.replace(
                f"RootPos = 0x{offsets.RootPos:X}",
                f"RootPos = 0x{rp_value:X}"
            )
            with open("lib/offsets.py", "w") as f:
                f.write(content)
            print(f"RootPos atualizado para 0x{rp_value:X}")
        except:
            print("Valor inválido. Nenhuma alteração foi feita.")
    
    return local_pawn


if __name__ == "__main__":
    find_local_player()
