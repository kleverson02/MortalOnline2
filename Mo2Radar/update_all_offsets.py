#!/usr/bin/env python3
from lib import offsets

# Valores comuns para offsets no UE5
common_offsets = {
    "ActorArray": [0xA0, 0xA8, 0xB0, 0xB8, 0xC0, 0xC8, 0xD0],
    "RootComponent": [0x190, 0x198, 0x1A0, 0x1A8, 0x1B0, 0x1B8, 0x1C0],
    "RootPos": [0xE0, 0xE8, 0xF0, 0xF8, 0x100, 0x108, 0x110, 0x118],
    "IsGhost": [0x670, 0x678, 0x680, 0x688, 0x690],
    "CreatureName": [0xC80, 0xC88, 0xC90, 0xC98, 0xCA0, 0xCA8],
    "Health": [0xCC0, 0xCC8, 0xCD0, 0xCD8, 0xCE0, 0xCE8],
    "MeshName": [0x2E0, 0x2E8, 0x2F0, 0x2F8, 0x300]
}

def update_offset(name, new_value):
    with open("lib/offsets.py", "r") as f:
        content = f.read()
    
    current_value = getattr(offsets, name)
    content = content.replace(
        f"{name} = 0x{current_value:X}",
        f"{name} = 0x{new_value:X}"
    )
    
    with open("lib/offsets.py", "w") as f:
        f.write(content)
    
    print(f"Offset {name} atualizado: 0x{current_value:X} -> 0x{new_value:X}")

def main():
    print("Ferramenta para atualizar todos os offsets para UE5")
    print("--------------------------------------------------")
    
    for name, values in common_offsets.items():
        current = getattr(offsets, name)
        print(f"\n{name} (atual: 0x{current:X}):")
        
        for i, value in enumerate(values):
            print(f"{i+1}. 0x{value:X}")
        
        choice = input(f"\nEscolha um valor para {name} (1-{len(values)}) ou pressione Enter para manter: ")
        if choice and choice.isdigit() and 1 <= int(choice) <= len(values):
            update_offset(name, values[int(choice)-1])

if __name__ == "__main__":
    main()