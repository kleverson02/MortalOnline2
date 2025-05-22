#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def find_camera_offsets():
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    print(f"UWorld: 0x{uworld:X}")
    
    # Obter o jogador local
    game_instance = mem.read(uworld + offsets.OwningGameInstance, "Q")
    local_players = mem.read(game_instance + offsets.LocalPlayers, "Q")
    local_player = mem.read(local_players, "Q")
    controller = mem.read(local_player + offsets.PlayerController, "Q")
    
    print(f"Controller: 0x{controller:X}")
    
    # Procurar por PlayerCameraManager
    print("\nProcurando PlayerCameraManager...")
    for offset in range(0x330, 0x370, 8):
        try:
            camera = mem.read(controller + offset, "Q")
            if camera and camera > 0x10000000:
                print(f"Possível PlayerCameraManager em 0x{offset:X}: 0x{camera:X}")
                
                # Verificar se parece ser um objeto válido
                try:
                    # Tentar ler alguns valores para ver se é um objeto válido
                    values = mem.read(camera, "8Q")
                    if any(0x10000000 < v < 0x7FFFFFFFFFFF for v in values):
                        print(f"  Parece ser um objeto válido")
                except:
                    pass
        except:
            pass
    
    # Perguntar qual offset usar
    camera_offset = input("\nDigite o offset para PlayerCameraManager (ex: 348): ")
    if not camera_offset:
        print("Nenhum offset fornecido. Saindo.")
        return
    
    try:
        camera_offset = int(camera_offset, 16)
        camera = mem.read(controller + camera_offset, "Q")
        print(f"Camera: 0x{camera:X}")
        
        # Procurar por CameraCachePrivate
        print("\nProcurando CameraCachePrivate...")
        for offset in range(0x1380, 0x1400, 8):
            try:
                # Tentar ler como float32
                values = mem.read(camera + offset, "6f")
                if any(v != 0 for v in values) and all(-1000000 < v < 1000000 for v in values):
                    print(f"Possível CameraCachePrivate em 0x{offset:X} (float32): {values}")
            except:
                pass
            
            try:
                # Tentar ler como float64
                values = mem.read(camera + offset, "6d")
                if any(v != 0 for v in values) and all(-1000000 < v < 1000000 for v in values):
                    print(f"Possível CameraCachePrivate em 0x{offset:X} (float64): {values}")
            except:
                pass
        
        # Procurar por AcknowledgedPawn
        print("\nProcurando AcknowledgedPawn...")
        for offset in range(0x330, 0x350, 8):
            try:
                pawn = mem.read(controller + offset, "Q")
                if pawn and pawn > 0x10000000:
                    print(f"Possível AcknowledgedPawn em 0x{offset:X}: 0x{pawn:X}")
                    
                    # Verificar se parece ser um objeto válido
                    try:
                        # Tentar ler alguns valores para ver se é um objeto válido
                        values = mem.read(pawn, "8Q")
                        if any(0x10000000 < v < 0x7FFFFFFFFFFF for v in values):
                            print(f"  Parece ser um objeto válido")
                    except:
                        pass
            except:
                pass
        
        # Perguntar quais offsets atualizar
        print("\nDigite os novos offsets (deixe em branco para manter o atual):")
        
        new_camera = input(f"PlayerCameraManager (atual: 0x{offsets.PlayerCameraManager:X}): ")
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
                print("Valor inválido. Nenhuma alteração feita.")
        
        new_cache = input(f"CameraCachePrivate (atual: 0x{offsets.CameraCachePrivate:X}): ")
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
                print("Valor inválido. Nenhuma alteração feita.")
        
        new_pawn = input(f"AcknowledgedPawn (atual: 0x{offsets.AcknowledgedPawn:X}): ")
        if new_pawn:
            try:
                pawn_offset = int(new_pawn, 16)
                with open("lib/offsets.py", "r") as f:
                    content = f.read()
                content = content.replace(
                    f"AcknowledgedPawn = 0x{offsets.AcknowledgedPawn:X}",
                    f"AcknowledgedPawn = 0x{pawn_offset:X}"
                )
                with open("lib/offsets.py", "w") as f:
                    f.write(content)
                print(f"AcknowledgedPawn atualizado para 0x{pawn_offset:X}")
            except:
                print("Valor inválido. Nenhuma alteração feita.")
        
        # Perguntar se deseja usar float32
        use_float32 = input("\nUsar float32 para leitura da câmera? (s/n): ").lower() == 's'
        if use_float32:
            with open("lib/game.py", "r") as f:
                content = f.read()
            if '"6df"' in content:
                content = content.replace('"6df"', '"6ff"')
                with open("lib/game.py", "w") as f:
                    f.write(content)
                print("Formato de leitura da câmera alterado para float32.")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    find_camera_offsets()