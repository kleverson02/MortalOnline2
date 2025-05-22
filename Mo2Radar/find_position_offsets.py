#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def find_position_offsets():
    mem = Reader("GameThread")
    uworld = mem.read(offsets.GWorld, "Q")
    persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
    
    # Lê o array de atores
    actor_array, actor_count = mem.read(persistent_level + offsets.ActorArray, "QI")
    
    print(f"GWorld: 0x{uworld:X}")
    print(f"PersistentLevel: 0x{persistent_level:X}")
    print(f"ActorArray: 0x{actor_array:X}")
    print(f"ActorCount: {actor_count}")
    
    # Testa diferentes offsets para RootComponent
    root_component_offsets = [0x1B8]
    root_pos_offsets = [0xF8]


    # Pega os primeiros 5 atores válidos
    actors = []
    for i in range(actor_count):
        actor = mem.read(actor_array + (i * 8), "Q")
        if actor > 0x10000000:
            actors.append(actor)
            if len(actors) >= 5:
                break
    
    print(f"\nEncontrados {len(actors)} atores para teste")
    
    # Testa cada combinação de offsets
    for rc_offset in root_component_offsets:
        for rp_offset in root_pos_offsets:
            print(f"\nTestando RootComponent=0x{rc_offset:X}, RootPos=0x{rp_offset:X}")
            try:
                for actor in actors:
                    root_component = mem.read(actor + rc_offset, "Q")                    

                    if root_component > 0x10000000:
                        pos = mem.read(root_component + rp_offset, "3d")
                        # Verifica se as coordenadas parecem válidas (dentro de limites razoáveis)
                        if all(-100000 < p < 100000 for p in pos):
                            print(f"  Actor: 0x{actor:X}")
                            print(f"  RootComponent: 0x{root_component:X}")
                            print(f"  Posição: {pos}")
                            return rc_offset, rp_offset
            except:
                continue
    
    return None, None

if __name__ == "__main__":
    rc_offset, rp_offset = find_position_offsets()
    if rc_offset and rp_offset:
        print(f"\nPossíveis offsets encontrados:")
        print(f"RootComponent = 0x{rc_offset:X}")
        print(f"RootPos = 0x{rp_offset:X}")
        
        update = input("\nAtualizar offsets.py? (s/n): ").lower() == 's'
        if update:
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            
            content = content.replace(
                f"RootComponent = 0x{offsets.RootComponent:X}",
                f"RootComponent = 0x{rc_offset:X}"
            )
            content = content.replace(
                f"RootPos = 0x{offsets.RootPos:X}",
                f"RootPos = 0x{rp_offset:X}"
            )
            
            with open("lib/offsets.py", "w") as f:
                f.write(content)
            print("Arquivo offsets.py atualizado!")
    else:
        print("\nNão foi possível encontrar os offsets de posição.")