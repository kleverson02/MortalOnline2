#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def find_player_position_offset():
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
                # Tentar ler o nome do jogador
                try:
                    name_addr, name_length = mem.read(actor + offsets.CreatureName, "QB")
                    if name_addr > 0x10000000 and 0 < name_length < 50:
                        name_bytes = max(0, name_length * 2 - 2)
                        name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
                        players.append((actor, name))
                except:
                    players.append((actor, "Desconhecido"))
                
                if len(players) >= 5:  # Limitar a 5 jogadores para análise
                    break
        except:
            continue
    
    if not players:
        print("Nenhum jogador encontrado.")
        return
    
    print(f"Encontrados {len(players)} jogadores para análise.")
    
    # Testar diferentes offsets para RootComponent
    for player_addr, player_name in players:
        print(f"\nJogador: {player_name} (0x{player_addr:X})")
        
        # Testar offsets para RootComponent
        for root_offset in range(0x180, 0x1E0, 8):
            try:
                root_component = mem.read(player_addr + root_offset, "Q")
                if root_component and root_component > 0x10000000:
                    print(f"  Possível RootComponent em 0x{root_offset:X}: 0x{root_component:X}")
                    
                    # Testar offsets para RootPos
                    for pos_offset in range(0xE0, 0x140, 8):
                        try:
                            pos = mem.read(root_component + pos_offset, "3d")
                            if all(-1000000 < p < 1000000 for p in pos) and any(p != 0 for p in pos):
                                print(f"    Possível posição em 0x{pos_offset:X}: {pos}")
                        except:
                            pass
            except:
                pass

def update_position_offsets():
    root_offset = input("\nDigite o novo offset para RootComponent (ex: 1A0): ")
    pos_offset = input("Digite o novo offset para RootPos (ex: F0): ")
    
    try:
        new_root_offset = int(root_offset, 16)
        new_pos_offset = int(pos_offset, 16)
        
        with open("lib/offsets.py", "r") as f:
            content = f.read()
        
        content = content.replace(
            f"RootComponent = 0x{offsets.RootComponent:X}",
            f"RootComponent = 0x{new_root_offset:X}"
        )
        content = content.replace(
            f"RootPos = 0x{offsets.RootPos:X}",
            f"RootPos = 0x{new_pos_offset:X}"
        )
        
        with open("lib/offsets.py", "w") as f:
            f.write(content)
        
        print(f"Offsets atualizados: RootComponent=0x{new_root_offset:X}, RootPos=0x{new_pos_offset:X}")
    except:
        print("Valores inválidos. Nenhuma alteração foi feita.")

if __name__ == "__main__":
    find_player_position_offset()
    
    update = input("\nDeseja atualizar os offsets de posição? (s/n): ").lower() == 's'
    if update:
        update_position_offsets()