#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def find_player_name_offset():
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
    
    # Ler o array de atores
    actor_array, actor_count = mem.read(persistent_level + offsets.ActorArray, "QI")
    
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
                players.append(actor)
                if len(players) >= 5:  # Limitar a 5 jogadores para análise
                    break
        except:
            continue
    
    if not players:
        print("Nenhum jogador encontrado.")
        return
    
    print(f"Encontrados {len(players)} jogadores para análise.")
    
    # Testar diferentes offsets para o nome do jogador
    for player_addr in players:
        print(f"\nJogador: 0x{player_addr:X}")
        
        # Testar uma faixa maior de offsets
        for offset in range(0xC80, 0xD20, 8):
            try:
                name_addr, name_length = mem.read(player_addr + offset, "QB")
                if name_addr > 0x10000000 and 0 < name_length < 50:
                    name_bytes = max(0, name_length * 2 - 2)
                    name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
                    if name and len(name) > 1:
                        print(f"  Offset 0x{offset:X}: {name}")
            except:
                pass

def update_creature_name_offset():
    offset = input("\nDigite o novo offset para CreatureName (ex: C90): ")
    
    try:
        new_offset = int(offset, 16)
        
        with open("lib/offsets.py", "r") as f:
            content = f.read()
        
        content = content.replace(
            f"CreatureName = 0x{offsets.CreatureName:X}",
            f"CreatureName = 0x{new_offset:X}"
        )
        
        with open("lib/offsets.py", "w") as f:
            f.write(content)
        
        print(f"Offset CreatureName atualizado para 0x{new_offset:X}")
    except:
        print("Valor inválido. Nenhuma alteração foi feita.")

if __name__ == "__main__":
    find_player_name_offset()
    
    update = input("\nDeseja atualizar o offset CreatureName? (s/n): ").lower() == 's'
    if update:
        update_creature_name_offset()