#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def test_simple_actor_positions():
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    if not uworld:
        print("Erro: Não foi possível ler GWorld")
        return
    
    print(f"GWorld: 0x{uworld:X}")
    
    # Obter PersistentLevel
    persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
    if not persistent_level:
        print("Erro: Não foi possível ler PersistentLevel")
        return
    
    print(f"PersistentLevel: 0x{persistent_level:X}")
    
    # Testar diferentes offsets para ActorArray
    for actor_array_offset in [0x90, 0x98, 0xA0, 0xA8, 0xB0, 0xB8, 0xC0, 0xC8, 0xD0]:
        try:
            actor_array, actor_count = mem.read(persistent_level + actor_array_offset, "QI")
            
            if actor_array > 0x10000000 and 0 < actor_count < 10000:
                print(f"\nTestando ActorArray offset 0x{actor_array_offset:X}")
                print(f"ActorArray: 0x{actor_array:X}")
                print(f"ActorCount: {actor_count}")
                
                # Testar diferentes offsets para RootComponent
                for root_offset in [0x190, 0x198, 0x1A0, 0x1A8, 0x1B0, 0x1B8, 0x1C0]:
                    # Testar diferentes offsets para RootPos
                    for pos_offset in [0xE0, 0xE8, 0xF0, 0xF8, 0x100, 0x108, 0x110, 0x118]:
                        valid_positions = 0
                        
                        # Verificar os primeiros 20 atores
                        for i in range(min(actor_count, 100)):
                            try:
                                actor = mem.read(actor_array + (i * 8), "Q")
                                if actor > 0x10000000:
                                    root_component = mem.read(actor + root_offset, "Q")
                                    if root_component and root_component > 0x10000000:
                                        pos = mem.read(root_component + pos_offset, "3d")
                                        if all(-1000000 < p < 1000000 for p in pos) and any(p != 0 for p in pos):
                                            valid_positions += 1
                                            
                                            if valid_positions <= 5:  # Mostrar apenas os primeiros 5
                                                print(f"Actor {i}: Pos={pos}")
                            except:
                                continue
                        
                        if valid_positions > 0:
                            print(f"Combinação encontrada: ActorArray=0x{actor_array_offset:X}, "
                                  f"RootComponent=0x{root_offset:X}, RootPos=0x{pos_offset:X}")
                            print(f"Posições válidas: {valid_positions}")
                            
                            # Perguntar se deseja atualizar os offsets
                            update = input("\nAtualizar offsets.py com estes valores? (s/n): ").lower() == 's'
                            if update:
                                with open("lib/offsets.py", "r") as f:
                                    content = f.read()
                                
                                content = content.replace(
                                    f"ActorArray = 0x{offsets.ActorArray:X}",
                                    f"ActorArray = 0x{actor_array_offset:X}"
                                )
                                content = content.replace(
                                    f"RootComponent = 0x{offsets.RootComponent:X}",
                                    f"RootComponent = 0x{root_offset:X}"
                                )
                                content = content.replace(
                                    f"RootPos = 0x{offsets.RootPos:X}",
                                    f"RootPos = 0x{pos_offset:X}"
                                )
                                
                                with open("lib/offsets.py", "w") as f:
                                    f.write(content)
                                
                                print("Offsets atualizados!")
                                return
        except:
            continue
    
    print("\nNenhuma combinação válida encontrada.")

if __name__ == "__main__":
    test_simple_actor_positions()