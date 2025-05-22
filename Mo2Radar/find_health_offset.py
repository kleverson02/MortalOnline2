#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def find_health_offset():
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
    
    # Ler o array de atores
    actor_array, actor_count = mem.read(persistent_level + offsets.ActorArray, "QI")
    print(f"Actor Array: 0x{actor_array:X}, Count: {actor_count}")
    
    # Encontrar jogadores
    players = []
    
    for i in range(min(actor_count, 1000)):
        actor = mem.read(actor_array + (i * 8), "Q")
        if not actor or actor < 0x10000000:
            continue
            
        try:
            # Ler o FName key
            key = mem.read(actor + 0x18, "2H")
            
            # Recuperar o nome do FName
            block = key[1] * 8
            offset = key[0] * 2
            
            block_ptr = mem.read(offsets.GNames + block, "Q")
            name_len = mem.read(block_ptr + offset, "H") >> 6
            fname = mem.read_string(block_ptr + offset + 2, name_len)
            
            # Verificar se é um jogador
            if "BP_PlayerCharacter_C" in fname:
                # Tentar ler o nome
                name = "Desconhecido"
                try:
                    name_addr, name_length = mem.read(actor + offsets.CreatureName, "QB")
                    if name_addr > 0x10000000 and 0 < name_length < 50:
                        name_bytes = max(0, name_length * 2 - 2)
                        name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
                except:
                    pass
                
                players.append((actor, name))
        except:
            continue
    
    # Testar diferentes offsets para Health
    print(f"\nJogadores encontrados: {len(players)}")
    
    for actor, name in players:
        print(f"\nTestando offsets para Health no jogador {name} (0x{actor:X}):")
        
        # Testar uma faixa de offsets
        for offset in range(0xCC0, 0xD20, 8):
            try:
                # Tentar ler como 2 floats (health, maxHealth)
                health, max_health = mem.read(actor + offset, "2f")
                
                # Verificar se os valores parecem razoáveis para saúde
                if 0 <= health <= max_health and max_health > 0 and max_health < 10000:
                    print(f"  Offset 0x{offset:X}: {health}/{max_health} (float32)")
            except:
                pass
                
            try:
                # Tentar ler como 2 doubles (health, maxHealth)
                health, max_health = mem.read(actor + offset, "2d")
                
                # Verificar se os valores parecem razoáveis para saúde
                if 0 <= health <= max_health and max_health > 0 and max_health < 10000:
                    print(f"  Offset 0x{offset:X}: {health}/{max_health} (float64)")
            except:
                pass
    
    # Perguntar qual offset usar
    new_offset = input("\nDigite o novo offset para Health (ou Enter para manter o atual): ")
    if new_offset:
        try:
            offset_value = int(new_offset, 16)
            
            # Atualizar o arquivo offsets.py
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            
            content = content.replace(
                f"Health = 0x{offsets.Health:X}",
                f"Health = 0x{offset_value:X}"
            )
            
            with open("lib/offsets.py", "w") as f:
                f.write(content)
            
            print(f"Offset Health atualizado para 0x{offset_value:X}")
        except:
            print("Valor inválido. Nenhuma alteração foi feita.")

if __name__ == "__main__":
    find_health_offset()
