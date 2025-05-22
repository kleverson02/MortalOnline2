#!/usr/bin/env python3
from lib import offsets

# Valores comuns para UE5
UE5_OFFSETS = {
    "PersistentLevel": 0x38,
    "ActorArray": 0xB8,
    "OwningGameInstance": 0x1E0,
    "LocalPlayers": 0x40,
    "PlayerController": 0x38,
    "PlayerCameraManager": 0x350,
    "CameraCachePrivate": 0x13A8,
    "AcknowledgedPawn": 0x340,
    "RootComponent": 0x1B0,
    "RootPos": 0x108,
    "IsGhost": 0x680,
    "CreatureName": 0xC88,
    "Health": 0xCD8
}

def update_offsets():
    print("Atualizando offsets para UE5...")
    
    with open("lib/offsets.py", "r") as f:
        content = f.read()
    
    # Atualizar cada offset
    for name, value in UE5_OFFSETS.items():
        current_value = getattr(offsets, name)
        content = content.replace(
            f"{name} = 0x{current_value:X}",
            f"{name} = 0x{value:X}"
        )
    
    with open("lib/offsets.py", "w") as f:
        f.write(content)
    
    # Atualizar formatos de leitura para float32
    with open("lib/game.py", "r") as f:
        game_content = f.read()
    
    if '"6df"' in game_content:
        game_content = game_content.replace('"6df"', '"6ff"')
        with open("lib/game.py", "w") as f:
            f.write(game_content)
    
    with open("lib/actors.py", "r") as f:
        actors_content = f.read()
    
    if '"3d"' in actors_content and 'self.pos = self.mem.read(' in actors_content:
        actors_content = actors_content.replace(
            'self.pos = self.mem.read(self.root_component + offsets.RootPos, "3d")',
            'self.pos = self.mem.read(self.root_component + offsets.RootPos, "3f")'
        )
        with open("lib/actors.py", "w") as f:
            f.write(actors_content)
    
    print("Offsets atualizados para UE5!")
    print("\nNovos valores:")
    for name, value in UE5_OFFSETS.items():
        print(f"{name} = 0x{value:X}")
    
    print("\nExecute 'python main.py' para testar o radar.")

if __name__ == "__main__":
    update_offsets()