#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def find_is_ghost_offset():
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
    
    # Tentar obter o jogador local
    try:
        game_instance = mem.read(uworld + offsets.OwningGameInstance, "Q")
        local_players = mem.read(game_instance + offsets.LocalPlayers, "Q")
        local_player = mem.read(local_players, "Q")
        controller = mem.read(local_player + offsets.PlayerController, "Q")
        local_pawn = mem.read(controller + offsets.AcknowledgedPawn, "Q")
        
        if local_pawn:
            print(f"Local Pawn: 0x{local_pawn:X}")
        else:
            print("Local Pawn não encontrado")
    except:
        print("Erro ao obter o jogador local")
        local_pawn = None
    
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
    
    # Testar diferentes offsets para IsGhost
    print(f"\nJogadores encontrados: {len(players)}")
    
    for actor, name in players:
        print(f"\nTestando offsets para IsGhost no jogador {name} (0x{actor:X}):")
        
        # Testar uma faixa de offsets
        for offset in range(0x650, 0x700, 8):
            try:
                # Tentar ler como booleano
                value = mem.read(actor + offset, "?")
                print(f"  Offset 0x{offset:X}: {value}")
                
                # Tentar ler como byte
                try:
                    byte_value = mem.read(actor + offset, "B")
                    if byte_value in [0, 1]:
                        print(f"  Offset 0x{offset:X} (byte): {byte_value}")
                except:
                    pass
            except:
                pass
    
    # Perguntar qual offset usar
    new_offset = input("\nDigite o novo offset para IsGhost (ou Enter para manter o atual): ")
    if new_offset:
        try:
            offset_value = int(new_offset, 16)
            
            # Atualizar o arquivo offsets.py
            with open("lib/offsets.py", "r") as f:
                content = f.read()
            
            content = content.replace(
                f"IsGhost = 0x{offsets.IsGhost:X}",
                f"IsGhost = 0x{offset_value:X}"
            )
            
            with open("lib/offsets.py", "w") as f:
                f.write(content)
            
            print(f"Offset IsGhost atualizado para 0x{offset_value:X}")
        except:
            print("Valor inválido. Nenhuma alteração foi feita.")

if __name__ == "__main__":
    find_is_ghost_offset()
