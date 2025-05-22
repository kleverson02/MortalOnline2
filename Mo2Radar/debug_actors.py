#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def find_player_controller_offset():
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    
    # Obter o OwningGameInstance
    game_instance = mem.read(uworld + offsets.OwningGameInstance, "Q")
    print(f"UWorld: 0x{uworld:X}")
    print(f"OwningGameInstance: 0x{game_instance:X}")
    
    # Obter o LocalPlayers
    local_players = mem.read(game_instance + offsets.LocalPlayers, "Q")
    print(f"LocalPlayers: 0x{local_players:X}")
    
    # Obter o primeiro jogador local
    local_player = mem.read(local_players, "Q")
    print(f"LocalPlayer: 0x{local_player:X}")
    
    # Testar diferentes offsets para PlayerController
    print("\nTestando offsets para PlayerController:")
    for offset in range(0x28, 0x50, 8):
        try:
            controller = mem.read(local_player + offset, "Q")
            if controller and controller > 0x10000000:
                print(f"Offset 0x{offset:X}: 0x{controller:X}")
                
                # Verificar se este controller tem um AcknowledgedPawn válido
                for pawn_offset in range(0x330, 0x350, 8):
                    try:
                        pawn = mem.read(controller + pawn_offset, "Q")
                        if pawn and pawn > 0x10000000:
                            print(f"  AcknowledgedPawn em 0x{pawn_offset:X}: 0x{pawn:X}")
                            
                            # Verificar se este pawn tem um RootComponent válido
                            for rc_offset in [0x188, 0x190, 0x198, 0x1A0, 0x1A8, 0x1B0, 0x1B8]:
                                try:
                                    root = mem.read(pawn + rc_offset, "Q")
                                    if root and root > 0x10000000:
                                        print(f"    RootComponent em 0x{rc_offset:X}: 0x{root:X}")
                                        
                                        # Verificar se este RootComponent tem uma posição válida
                                        for pos_offset in [0xE0, 0xE8, 0xF0, 0xF8, 0x100, 0x108, 0x110]:
                                            try:
                                                pos = mem.read(root + pos_offset, "3f")
                                                if any(p != 0 for p in pos) and all(-1000000 < p < 1000000 for p in pos):
                                                    print(f"      Posição em 0x{pos_offset:X} (float32): {pos}")
                                            except:
                                                pass
                                            
                                            try:
                                                pos = mem.read(root + pos_offset, "3d")
                                                if any(p != 0 for p in pos) and all(-1000000 < p < 1000000 for p in pos):
                                                    print(f"      Posição em 0x{pos_offset:X} (float64): {pos}")
                                            except:
                                                pass
                                except:
                                    pass
                    except:
                        pass
        except:
            pass
    
    # Verificar o offset atual
    print(f"\nOffset atual para PlayerController: 0x{offsets.PlayerController:X}")
    
    # Perguntar se deseja atualizar o offset
    new_offset = input("\nDigite o novo offset para PlayerController (ou Enter para manter o atual): ")
    if new_offset:
        try:
            offset_value = int(new_offset, 16)
            
            # Atualizar o arquivo offsets.py
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            
            content = content.replace(
                f"PlayerController = 0x{offsets.PlayerController:X}",
                f"PlayerController = 0x{offset_value:X}"
            )
            
            with open("lib/offsets.py", "w") as f:
                f.write(content)
            
            print(f"Offset PlayerController atualizado para 0x{offset_value:X}")
        except:
            print("Valor inválido. Nenhuma alteração foi feita.")

if __name__ == "__main__":
    find_player_controller_offset()
