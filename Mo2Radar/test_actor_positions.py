#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def test_actor_positions():
    mem = Reader("GameThread")
    uworld = mem.read(offsets.GWorld, "Q")
    persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
    
    # Lê o array de atores
    actor_array, actor_count = mem.read(persistent_level + offsets.ActorArray, "QI")
    
    print(f"GWorld: 0x{uworld:X}")
    print(f"PersistentLevel: 0x{persistent_level:X}")
    print(f"ActorArray: 0x{actor_array:X}")
    print(f"ActorCount: {actor_count}")
    
    # Pega os primeiros 10 atores válidos
    actors = []
    for i in range(min(actor_count, 100)):
        actor = mem.read(actor_array + (i * 8), "Q")
        if actor > 0x10000000:
            actors.append(actor)
            if len(actors) >= 10:
                break
    
    print(f"\nEncontrados {len(actors)} atores para teste")
    
    # Testa os offsets atuais
    print(f"\nTestando com os offsets atuais:")
    print(f"RootComponent = 0x{offsets.RootComponent:X}")
    print(f"RootPos = 0x{offsets.RootPos:X}")
    
    for i, actor in enumerate(actors):
        try:
            # Tenta ler o nome do ator (se for um jogador ou NPC)
            try:
                key = mem.read(actor + 0x18, "2H")
                # Tenta ler o nome da criatura
                name_addr, name_length = mem.read(actor + offsets.CreatureName, "QB")
                if name_addr > 0x10000000 and name_length < 50:
                    name_bytes = max(0, name_length * 2 - 2)
                    name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
                    print(f"\nAtor {i+1}: 0x{actor:X} - Nome: {name}")
                else:
                    print(f"\nAtor {i+1}: 0x{actor:X}")
            except:
                print(f"\nAtor {i+1}: 0x{actor:X}")
            
            # Lê o RootComponent
            root_component = mem.read(actor + offsets.RootComponent, "Q")
            print(f"  RootComponent: 0x{root_component:X}")
            
            if root_component > 0x10000000:
                # Lê a posição
                pos = mem.read(root_component + offsets.RootPos, "3d")
                print(f"  Posição: {pos}")
            else:
                print("  RootComponent inválido")
        except Exception as e:
            print(f"  Erro ao ler ator: {e}")

if __name__ == "__main__":
    test_actor_positions()