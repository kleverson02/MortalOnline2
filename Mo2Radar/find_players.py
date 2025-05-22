#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def find_players():
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
    
    # Obter o jogador local
    game_instance = mem.read(uworld + offsets.OwningGameInstance, "Q")
    local_players = mem.read(game_instance + offsets.LocalPlayers, "Q")
    local_player = mem.read(local_players, "Q")
    controller = mem.read(local_player + offsets.PlayerController, "Q")
    local_pawn = mem.read(controller + offsets.AcknowledgedPawn, "Q")
    
    print(f"UWorld: 0x{uworld:X}")
    print(f"PersistentLevel: 0x{persistent_level:X}")
    print(f"Local Pawn: 0x{local_pawn:X}")
    
    # Ler o array de atores
    actor_array, actor_count = mem.read(persistent_level + offsets.ActorArray, "QI")
    print(f"Actor Array: 0x{actor_array:X}")
    print(f"Actor Count: {actor_count}")
    
    # Procurar por todos os tipos de atores
    actor_types = {}
    player_candidates = []
    
    for i in range(min(actor_count, 500)):
        try:
            actor = mem.read(actor_array + (i * 8), "Q")
            if not actor or actor < 0x10000000:
                continue
                
            # Ler o FName key
            key = mem.read(actor + 0x18, "2H")
            
            # Recuperar o nome do FName
            block = key[1] * 8
            offset = key[0] * 2
            
            block_ptr = mem.read(offsets.GNames + block, "Q")
            name_len = mem.read(block_ptr + offset, "H") >> 6
            fname = mem.read_string(block_ptr + offset + 2, name_len)
            
            # Contar tipos de atores
            if fname not in actor_types:
                actor_types[fname] = 0
            actor_types[fname] += 1
            
            # Procurar por possíveis jogadores
            if "Character" in fname or "Player" in fname:
                player_candidates.append((actor, fname))
        except:
            continue
    
    # Mostrar tipos de atores mais comuns
    print("\nTipos de atores mais comuns:")
    for fname, count in sorted(actor_types.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"{fname}: {count}")
    
    # Analisar possíveis jogadores
    print("\nPossíveis jogadores encontrados:")
    for actor, fname in player_candidates:
        print(f"\nAtor: 0x{actor:X}, Tipo: {fname}")
        
        # Tentar ler o nome
        try:
            for name_offset in [offsets.CreatureName, offsets.CreatureName - 8, offsets.CreatureName + 8]:
                try:
                    name_addr, name_length = mem.read(actor + name_offset, "QB")
                    if name_addr > 0x10000000 and 0 < name_length < 50:
                        name_bytes = max(0, name_length * 2 - 2)
                        name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
                        print(f"  Nome (offset 0x{name_offset:X}): {name}")
                except:
                    pass
        except:
            pass
        
        # Tentar ler o RootComponent
        try:
            for root_offset in [0x188, 0x190, 0x198, 0x1A0, 0x1A8, 0x1B0, 0x1B8]:
                try:
                    root = mem.read(actor + root_offset, "Q")
                    if root and root > 0x10000000:
                        print(f"  RootComponent (offset 0x{root_offset:X}): 0x{root:X}")
                        
                        # Tentar ler a posição
                        for pos_offset in [0xE8, 0xF0, 0xF8, 0x100, 0x108, 0x110]:
                            try:
                                pos = mem.read(root + pos_offset, "3d")
                                if all(-1000000 < p < 1000000 for p in pos) and any(p != 0 for p in pos):
                                    print(f"    Posição (offset 0x{pos_offset:X}): {pos}")
                            except:
                                pass
                except:
                    pass
        except:
            pass
    
    # Perguntar se deseja atualizar os offsets
    print("\nCom base nos resultados acima, você pode atualizar os offsets manualmente.")
    print("Atual RootComponent: 0x{:X}".format(offsets.RootComponent))
    print("Atual RootPos: 0x{:X}".format(offsets.RootPos))
    
    update = input("\nDeseja atualizar os offsets? (s/n): ").lower() == 's'
    if update:
        new_root = input("Novo offset para RootComponent (ex: 1A0): ")
        new_pos = input("Novo offset para RootPos (ex: F8): ")
        
        try:
            root_offset = int(new_root, 16)
            pos_offset = int(new_pos, 16)
            
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            
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
        except:
            print("Valores inválidos. Nenhuma alteração foi feita.")

if __name__ == "__main__":
    find_players()