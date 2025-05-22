#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def test_local_player_position():
    mem = Reader("GameThread")
    uworld = mem.read(offsets.GWorld, "Q")
    
    # Obter o jogador local
    game_instance = mem.read(uworld + offsets.OwningGameInstance, "Q")
    local_players = mem.read(game_instance + offsets.LocalPlayers, "Q")
    local_player = mem.read(local_players, "Q")
    controller = mem.read(local_player + offsets.PlayerController, "Q")
    local_pawn = mem.read(controller + offsets.AcknowledgedPawn, "Q")
    
    print(f"Local Pawn: 0x{local_pawn:X}")
    
    if local_pawn:
        # Testar o offset atual do RootComponent
        root_component = mem.read(local_pawn + offsets.RootComponent, "Q")
        print(f"RootComponent: 0x{root_component:X}")
        
        if root_component:
            # Testar diferentes offsets para RootPos
            for offset in range(0xE0, 0x140, 8):
                try:
                    pos = mem.read(root_component + offset, "3d")
                    if any(p != 0 for p in pos) and all(-1000000 < p < 1000000 for p in pos):
                        print(f"Offset 0x{offset:X}: {pos}")
                except:
                    pass

if __name__ == "__main__":
    test_local_player_position()