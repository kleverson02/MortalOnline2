#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def confirm_controller_camera_offsets():
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    print(f"UWorld: 0x{uworld:X}")
    
    # Obter o OwningGameInstance
    game_instance = mem.read(uworld + offsets.OwningGameInstance, "Q")
    print(f"OwningGameInstance (0x{offsets.OwningGameInstance:X}): 0x{game_instance:X}")
    
    # Obter o LocalPlayers
    local_players = mem.read(game_instance + offsets.LocalPlayers, "Q")
    print(f"LocalPlayers (0x{offsets.LocalPlayers:X}): 0x{local_players:X}")
    
    # Testar diferentes offsets para LocalPlayer
    print("\nTestando offsets para LocalPlayer:")
    for offset in range(0x30, 0x50, 8):
        try:
            local_player = mem.read(local_players + offset, "Q")
            if local_player and local_player > 0x10000000 and local_player < 0x7FFFFFFFFFFF:
                print(f"LocalPlayer em 0x{offset:X}: 0x{local_player:X}")
                
                # Testar diferentes offsets para PlayerController
                print(f"\nTestando offsets para PlayerController a partir de LocalPlayer 0x{local_player:X}:")
                for pc_offset in range(0x28, 0x40, 8):
                    try:
                        controller = mem.read(local_player + pc_offset, "Q")
                        if controller and controller > 0x10000000 and controller < 0x7FFFFFFFFFFF:
                            print(f"PlayerController em 0x{pc_offset:X}: 0x{controller:X}")
                            
                            # Testar diferentes offsets para PlayerCameraManager
                            print(f"\nTestando offsets para PlayerCameraManager a partir de Controller 0x{controller:X}:")
                            for cam_offset in range(0x340, 0x360, 8):
                                try:
                                    camera = mem.read(controller + cam_offset, "Q")
                                    if camera and camera > 0x10000000 and camera < 0x7FFFFFFFFFFF:
                                        print(f"PlayerCameraManager em 0x{cam_offset:X}: 0x{camera:X}")
                                        
                                        # Verificar se este camera tem um CameraCachePrivate válido
                                        for cache_offset in range(0x1380, 0x1400, 8):
                                            try:
                                                # Tentar ler como float32
                                                values = mem.read(camera + cache_offset, "6f")
                                                if any(v != 0 for v in values) and all(-1000000 < v < 1000000 for v in values):
                                                    print(f"  CameraCachePrivate em 0x{cache_offset:X} (float32): {values}")
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
    
    new_cam = input(f"PlayerCameraManager (atual: 0x{offsets.PlayerCameraManager:X}): ")
    if new_cam:
        try:
            cam_value = int(new_cam, 16)
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            content = content.replace(
                f"PlayerCameraManager = 0x{offsets.PlayerCameraManager:X}",
                f"PlayerCameraManager = 0x{cam_value:X}"
            )
            with open("lib/offsets.py", "w") as f:
                f.write(content)
            print(f"PlayerCameraManager atualizado para 0x{cam_value:X}")
        except:
            print("Valor inválido. Nenhuma alteração foi feita.")

if __name__ == "__main__":
    confirm_controller_camera_offsets()
