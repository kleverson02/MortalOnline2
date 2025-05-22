#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def find_player_chain_offsets():
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    print(f"UWorld: 0x{uworld:X}")
    
    # Testar diferentes offsets para OwningGameInstance
    print("\nTestando offsets para OwningGameInstance:")
    for offset in range(0x1C0, 0x200, 8):
        try:
            game_instance = mem.read(uworld + offset, "Q")
            if game_instance and game_instance > 0x10000000 and game_instance < 0x7FFFFFFFFFFF:
                print(f"Offset 0x{offset:X}: 0x{game_instance:X}")
                
                # Testar LocalPlayers para este OwningGameInstance
                for lp_offset in range(0x30, 0x50, 8):
                    try:
                        local_players = mem.read(game_instance + lp_offset, "Q")
                        if local_players and local_players > 0x10000000 and local_players < 0x7FFFFFFFFFFF:
                            print(f"  LocalPlayers em 0x{lp_offset:X}: 0x{local_players:X}")
                            
                            # Obter o primeiro jogador local
                            local_player = mem.read(local_players, "Q")
                            if local_player and local_player > 0x10000000 and local_player < 0x7FFFFFFFFFFF:
                                print(f"  LocalPlayer: 0x{local_player:X}")
                                
                                # Testar PlayerController para este LocalPlayer
                                for pc_offset in range(0x28, 0x40, 8):
                                    try:
                                        controller = mem.read(local_player + pc_offset, "Q")
                                        if controller and controller > 0x10000000 and controller < 0x7FFFFFFFFFFF:
                                            print(f"    PlayerController em 0x{pc_offset:X}: 0x{controller:X}")
                                            
                                            # Testar AcknowledgedPawn para este PlayerController
                                            for pawn_offset in range(0x330, 0x350, 8):
                                                try:
                                                    pawn = mem.read(controller + pawn_offset, "Q")
                                                    if pawn and pawn > 0x10000000 and pawn < 0x7FFFFFFFFFFF:
                                                        print(f"      AcknowledgedPawn em 0x{pawn_offset:X}: 0x{pawn:X}")
                                                        
                                                        # Verificar se este pawn tem um RootComponent válido
                                                        try:
                                                            root = mem.read(pawn + offsets.RootComponent, "Q")
                                                            if root and root > 0x10000000:
                                                                print(f"        RootComponent: 0x{root:X}")
                                                                
                                                                # Verificar se este RootComponent tem uma posição válida
                                                                try:
                                                                    pos = mem.read(root + offsets.RootPos, "3f")
                                                                    print(f"        Posição: {pos}")
                                                                except:
                                                                    pass
                                                        except:
                                                            pass
                                                except:
                                                    pass
                                    except:
                                        pass
                    except:
                        pass
        except:
            pass
    
    # Perguntar quais offsets atualizar
    print("\nDigite os novos offsets (deixe em branco para manter o atual):")
    
    new_ogi = input(f"OwningGameInstance (atual: 0x{offsets.OwningGameInstance:X}): ")
    if new_ogi:
        try:
            ogi_value = int(new_ogi, 16)
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            content = content.replace(
                f"OwningGameInstance = 0x{offsets.OwningGameInstance:X}",
                f"OwningGameInstance = 0x{ogi_value:X}"
            )
            with open("lib/offsets.py", "w") as f:
                f.write(content)
            print(f"OwningGameInstance atualizado para 0x{ogi_value:X}")
        except:
            print("Valor inválido. Nenhuma alteração foi feita.")
    
    new_lp = input(f"LocalPlayers (atual: 0x{offsets.LocalPlayers:X}): ")
    if new_lp:
        try:
            lp_value = int(new_lp, 16)
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            content = content.replace(
                f"LocalPlayers = 0x{offsets.LocalPlayers:X}",
                f"LocalPlayers = 0x{lp_value:X}"
            )
            with open("lib/offsets.py", "w") as f:
                f.write(content)
            print(f"LocalPlayers atualizado para 0x{lp_value:X}")
        except:
            print("Valor inválido. Nenhuma alteração foi feita.")
    
    new_pc = input(f"PlayerController (atual: 0x{offsets.PlayerController:X}): ")
    if new_pc:
        try:
            pc_value = int(new_pc, 16)
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            content = content.replace(
                f"PlayerController = 0x{offsets.PlayerController:X}",
                f"PlayerController = 0x{pc_value:X}"
            )
            with open("lib/offsets.py", "w") as f:
                f.write(content)
            print(f"PlayerController atualizado para 0x{pc_value:X}")
        except:
            print("Valor inválido. Nenhuma alteração foi feita.")
    
    new_pawn = input(f"AcknowledgedPawn (atual: 0x{offsets.AcknowledgedPawn:X}): ")
    if new_pawn:
        try:
            pawn_value = int(new_pawn, 16)
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            content = content.replace(
                f"AcknowledgedPawn = 0x{offsets.AcknowledgedPawn:X}",
                f"AcknowledgedPawn = 0x{pawn_value:X}"
            )
            with open("lib/offsets.py", "w") as f:
                f.write(content)
            print(f"AcknowledgedPawn atualizado para 0x{pawn_value:X}")
        except:
            print("Valor inválido. Nenhuma alteração foi feita.")

if __name__ == "__main__":
    find_player_chain_offsets()
