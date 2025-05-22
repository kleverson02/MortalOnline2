#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def find_acknowledged_pawn_offset():
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    
    # Obter o OwningGameInstance
    game_instance = mem.read(uworld + offsets.OwningGameInstance, "Q")
    print(f"UWorld: 0x{uworld:X}")
    print(f"OwningGameInstance: 0x{game_instance:X}")
    
    # Obter o LocalPlayers
    local_players = mem.read(game_instance + offsets.LocalPlayers, "Q")
    print(f"LocalPlayers: 0x{local_players:X}")
    
    # Obter o primeiro jogador local
    local_player = mem.read(local_players, "Q")
    print(f"LocalPlayer: 0x{local_player:X}")
    
    # Obter o PlayerController
    controller = mem.read(local_player + offsets.PlayerController, "Q")
    print(f"PlayerController: 0x{controller:X}")
    
    # Testar diferentes offsets para AcknowledgedPawn
    print("\nTestando offsets para AcknowledgedPawn:")
    
    # Ler o array de atores para verificar se o pawn encontrado é válido
    persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
    actor_array, actor_count = mem.read(persistent_level + offsets.ActorArray, "QI")
    
    # Ler todos os atores para verificação posterior
    actors = []
    for i in range(min(actor_count, 1000)):
        actor = mem.read(actor_array + (i * 8), "Q")
        if actor and actor > 0x10000000:
            actors.append(actor)
    
    print(f"Total de atores: {len(actors)}")
    
    # Testar diferentes offsets
    valid_offsets = []
    
    for offset in range(0x330, 0x350, 8):
        try:
            pawn = mem.read(controller + offset, "Q")
            if pawn and pawn > 0x10000000:
                print(f"Offset 0x{offset:X}: 0x{pawn:X}")
                
                # Verificar se este pawn está na lista de atores
                if pawn in actors:
                    print(f"  Este pawn está na lista de atores!")
                    valid_offsets.append((offset, pawn))
                    
                    # Verificar se este pawn tem um RootComponent válido
                    try:
                        root = mem.read(pawn + offsets.RootComponent, "Q")
                        if root and root > 0x10000000:
                            print(f"  RootComponent: 0x{root:X}")
                            
                            # Verificar se este RootComponent tem uma posição válida
                            try:
                                pos = mem.read(root + offsets.RootPos, "3f")
                                print(f"  Posição: {pos}")
                            except:
                                pass
                    except:
                        pass
                    
                    # Verificar se este pawn tem um nome
                    try:
                        name_addr, name_length = mem.read(pawn + offsets.CreatureName, "QB")
                        if name_addr > 0x10000000 and 0 < name_length < 50:
                            name_bytes = max(0, name_length * 2 - 2)
                            name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
                            print(f"  Nome: {name}")
                    except:
                        pass
        except:
            pass
    
    # Recomendar o melhor offset
    if valid_offsets:
        print("\nOffsets válidos encontrados:")
        for offset, pawn in valid_offsets:
            print(f"0x{offset:X}: 0x{pawn:X}")
        
        # Perguntar qual offset usar
        new_offset = input("\nDigite o novo offset para AcknowledgedPawn (ou Enter para manter o atual): ")
        if new_offset:
            try:
                offset_value = int(new_offset, 16)
                
                # Atualizar o arquivo offsets.py
                with open("lib/offsets.py", "r") as f:
                    content = f.read()
                
                content = content.replace(
                    f"AcknowledgedPawn = 0x{offsets.AcknowledgedPawn:X}",
                    f"AcknowledgedPawn = 0x{offset_value:X}"
                )
                
                with open("lib/offsets.py", "w") as f:
                    f.write(content)
                
                print(f"Offset AcknowledgedPawn atualizado para 0x{offset_value:X}")
            except:
                print("Valor inválido. Nenhuma alteração foi feita.")
    else:
        print("\nNenhum offset válido encontrado.")

if __name__ == "__main__":
    find_acknowledged_pawn_offset()
