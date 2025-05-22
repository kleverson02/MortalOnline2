#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def test_camera():
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    
    # Obter o jogador local
    game_instance = mem.read(uworld + offsets.OwningGameInstance, "Q")
    local_players = mem.read(game_instance + offsets.LocalPlayers, "Q")
    local_player = mem.read(local_players, "Q")
    controller = mem.read(local_player + offsets.PlayerController, "Q")
    
    print(f"Controller: 0x{controller:X}")
    
    # Verificar o PlayerCameraManager
    for offset in range(0x330, 0x360, 8):
        try:
            camera = mem.read(controller + offset, "Q")
            if camera and camera > 0x10000000:
                print(f"Possível PlayerCameraManager em 0x{offset:X}: 0x{camera:X}")
                
                # Testar CameraCachePrivate
                for cache_offset in range(0x1380, 0x1400, 8):
                    try:
                        raw_pov = mem.read(camera + cache_offset, "6f")
                        if all(-1000 < p < 1000 for p in raw_pov):
                            print(f"  Possível CameraCachePrivate em 0x{cache_offset:X}: {raw_pov}")
                    except:
                        pass
        except:
            pass
    
    # Testar o offset atual
    try:
        camera = mem.read(controller + offsets.PlayerCameraManager, "Q")
        print(f"\nPlayerCameraManager atual (0x{offsets.PlayerCameraManager:X}): 0x{camera:X}")
        
        raw_pov = mem.read(camera + offsets.CameraCachePrivate, "6f")
        print(f"CameraCachePrivate atual (0x{offsets.CameraCachePrivate:X}): {raw_pov}")
    except Exception as e:
        print(f"Erro ao ler com os offsets atuais: {e}")
    
    # Atualizar os offsets
    print("\nDigite os novos offsets:")
    new_camera = input(f"PlayerCameraManager (atual: 0x{offsets.PlayerCameraManager:X}): ")
    new_cache = input(f"CameraCachePrivate (atual: 0x{offsets.CameraCachePrivate:X}): ")
    
    if new_camera:
        try:
            camera_offset = int(new_camera, 16)
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            content = content.replace(
                f"PlayerCameraManager = 0x{offsets.PlayerCameraManager:X}",
                f"PlayerCameraManager = 0x{camera_offset:X}"
            )
            with open("lib/offsets.py", "w") as f:
                f.write(content)
            print(f"PlayerCameraManager atualizado para 0x{camera_offset:X}")
        except:
            print("Valor inválido para PlayerCameraManager.")
    
    if new_cache:
        try:
            cache_offset = int(new_cache, 16)
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            content = content.replace(
                f"CameraCachePrivate = 0x{offsets.CameraCachePrivate:X}",
                f"CameraCachePrivate = 0x{cache_offset:X}"
            )
            with open("lib/offsets.py", "w") as f:
                f.write(content)
            print(f"CameraCachePrivate atualizado para 0x{cache_offset:X}")
        except:
            print("Valor inválido para CameraCachePrivate.")

if __name__ == "__main__":
    test_camera()