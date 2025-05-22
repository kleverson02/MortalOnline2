#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def test_actor_array():
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
    
    print(f"UWorld: 0x{uworld:X}")
    print(f"PersistentLevel: 0x{persistent_level:X}")
    
    # Testar diferentes offsets para ActorArray
    for offset in [0x98, 0xA0, 0xA8, 0xB0, 0xB8, 0xC0, 0xC8]:
        try:
            actor_array, actor_count = mem.read(persistent_level + offset, "QI")
            if actor_array > 0x10000000 and 0 < actor_count < 10000:
                print(f"\nPossível ActorArray em 0x{offset:X}:")
                print(f"  Array: 0x{actor_array:X}")
                print(f"  Count: {actor_count}")
                
                # Verificar alguns atores
                valid_actors = 0
                player_count = 0
                
                for i in range(min(actor_count, 100)):
                    try:
                        actor = mem.read(actor_array + (i * 8), "Q")
                        if actor and actor > 0x10000000:
                            valid_actors += 1
                            
                            # Verificar se é um jogador
                            try:
                                key = mem.read(actor + 0x18, "2H")
                                block = key[1] * 8
                                key_offset = key[0] * 2
                                block_ptr = mem.read(offsets.GNames + block, "Q")
                                name_len = mem.read(block_ptr + key_offset, "H") >> 6
                                fname = mem.read_string(block_ptr + key_offset + 2, name_len)
                                
                                if "BP_PlayerCharacter_C" in fname:
                                    player_count += 1
                            except:
                                pass
                    except:
                        pass
                
                print(f"  Atores válidos nos primeiros 100: {valid_actors}")
                print(f"  Jogadores encontrados: {player_count}")
                
                if player_count > 0:
                    print(f"\n*** Offset 0x{offset:X} parece ser o correto! ***")
                    
                    # Perguntar se deseja atualizar o offset
                    update = input("\nAtualizar ActorArray para 0x{:X}? (s/n): ".format(offset))
                    if update.lower() == 's':
                        with open("lib/offsets.py", "r") as f:
                            content = f.read()
                        
                        content = content.replace(
                            f"ActorArray = 0x{offsets.ActorArray:X}",
                            f"ActorArray = 0x{offset:X}"
                        )
                        
                        with open("lib/offsets.py", "w") as f:
                            f.write(content)
                        
                        print(f"ActorArray atualizado para 0x{offset:X}")
        except:
            pass

if __name__ == "__main__":
    test_actor_array()