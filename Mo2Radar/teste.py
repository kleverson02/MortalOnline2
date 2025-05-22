#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets
import time
import math

def distance(pos1, pos2):
    """Calcula a distância entre duas posições 3D"""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(pos1, pos2)))

def find_player_by_name(name="Pombagira"):
    """Encontra um jogador pelo nome"""
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
    
    # Ler o array de atores
    actor_array, actor_count = mem.read(persistent_level + offsets.ActorArray, "QI")
    
    print(f"Procurando jogador com nome '{name}'...")
    
    # Obter o jogador local para diferentes offsets de AcknowledgedPawn
    game_instance = mem.read(uworld + offsets.OwningGameInstance, "Q")
    local_players = mem.read(game_instance + offsets.LocalPlayers, "Q")
    local_player = mem.read(local_players, "Q")
    controller = mem.read(local_player + offsets.PlayerController, "Q")
    
    # Testar diferentes offsets para AcknowledgedPawn
    possible_local_pawns = {}
    for pawn_offset in range(0x340, 0x350, 8):
        try:
            pawn = mem.read(controller + pawn_offset, "Q")
            if pawn and pawn > 0x10000000:
                possible_local_pawns[pawn_offset] = pawn
                print(f"Possível AcknowledgedPawn em 0x{pawn_offset:X}: 0x{pawn:X}")
        except:
            pass
    
    # Procurar por todos os jogadores
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
            if "BP_PlayerCharacter" in fname or "Character" in fname:
                # Tentar ler o nome do jogador
                player_name = None
                try:
                    for name_offset in [offsets.CreatureName, offsets.CreatureName - 8, offsets.CreatureName + 8]:
                        try:
                            name_addr, name_length = mem.read(actor + name_offset, "QB")
                            if name_addr > 0x10000000 and 0 < name_length < 50:
                                name_bytes = max(0, name_length * 2 - 2)
                                player_name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
                                if player_name and player_name == name:
                                    # Encontramos o jogador!
                                    print(f"Jogador '{name}' encontrado! Endereço: 0x{actor:X}")
                                    
                                    # Testar diferentes offsets para RootComponent
                                    print("\nTestando offsets para RootComponent:")
                                    for rc_offset in [0x188, 0x190, 0x198, 0x1A0, 0x1A8, 0x1B0, 0x1B8]:
                                        try:
                                            root = mem.read(actor + rc_offset, "Q")
                                            if root and root > 0x10000000:
                                                print(f"  RootComponent em 0x{rc_offset:X}: 0x{root:X}")
                                                
                                                # Testar diferentes offsets para RootPos
                                                for pos_offset in [0xE0, 0xE8, 0xF0, 0xF8, 0x100, 0x108, 0x110]:
                                                   
                                                        
                                                    try:
                                                        # Tentar como float64
                                                        pos = mem.read(root + pos_offset, "3d")
                                                        if any(p != 0 for p in pos) and all(-1000000 < p < 1000000 for p in pos):
                                                            print(f"    Posição em 0x{pos_offset:X} (float64): {pos}")
                                                    except:
                                                        pass
                                        except:
                                            pass
                                    
                                    # Verificar se é o jogador local para cada possível offset
                                    print("\nVerificando se é o jogador local:")
                                    is_local = False
                                    print(actor,local_pawn)
                                    for pawn_offset, local_pawn in possible_local_pawns.items():
                                        if actor == local_pawn:
                                            print(f"Este É o jogador local! (AcknowledgedPawn em 0x{pawn_offset:X})")
                                            is_local = True
                                            
                                            # Atualizar o offset no arquivo offsets.py
                                            update = input(f"Atualizar AcknowledgedPawn para 0x{pawn_offset:X}? (s/n): ")
                                            if update.lower() == 's':
                                                with open("lib/offsets.py", "r") as f:
                                                    content = f.read()
                                                content = content.replace(
                                                    f"AcknowledgedPawn = 0x{offsets.AcknowledgedPawn:X}",
                                                    f"AcknowledgedPawn = 0x{pawn_offset:X}"
                                                )
                                                with open("lib/offsets.py", "w") as f:
                                                    f.write(content)
                                                print(f"AcknowledgedPawn atualizado para 0x{pawn_offset:X}")
                                    
                                    if not is_local:
                                        print("Este NÃO é o jogador local.")
                                    
                                    return actor
                        except:
                            pass
                except:
                    pass
        except:
            continue
    
    print(f"Jogador '{name}' não encontrado.")
    return None


def show_player_positions():
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
    
    # Obter a posição do jogador local
    local_root = mem.read(local_pawn + offsets.RootComponent, "Q")
    local_pos = mem.read(local_root + offsets.RootPos, "3d")
    
    print(f"Posição do jogador local: {local_pos}")
    
    # Ler o array de atores
    actor_array, actor_count = mem.read(persistent_level + offsets.ActorArray, "QI")
    
    # Encontrar jogadores
    players = []
    
    for i in range(min(actor_count, 1000)):
        actor = mem.read(actor_array + (i * 8), "Q")
        if not actor or actor == local_pawn or actor < 0x10000000:
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
                # Tentar ler o RootComponent
                root_component = mem.read(actor + offsets.RootComponent, "Q")
                if not root_component or root_component < 0x10000000:
                    continue
                    
                # Ler a posição
                pos = mem.read(root_component + offsets.RootPos, "3d")
                
                # Verificar se a posição parece válida
                if not all(-1000000 < p < 1000000 for p in pos):
                    continue
                    
                # Calcular distância até o jogador local
                dist = distance(local_pos, pos)
                
                # Tentar ler o nome do jogador
                player_name = "Desconhecido"
                try:
                    for name_offset in [offsets.CreatureName, offsets.CreatureName - 8, offsets.CreatureName + 8]:
                        try:
                            name_addr, name_length = mem.read(actor + name_offset, "QB")
                            if name_addr > 0x10000000 and 0 < name_length < 50:
                                name_bytes = max(0, name_length * 2 - 2)
                                name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
                                if name and len(name) > 1:
                                    player_name = name
                                    break
                        except:
                            pass
                except:
                    pass
                
                players.append((actor, player_name, pos, dist))
        except:
            continue
    
    # Mostrar jogadores encontrados (ordenados por distância)
    print(f"\nJogadores encontrados: {len(players)}")
    for i, (addr, name, pos, dist) in enumerate(sorted(players, key=lambda x: x[3])):
        print(f"{i+1}. {name} (0x{addr:X})")
        print(f"   Posição: {pos}")
        print(f"   Distância: {dist:.1f}")
        
        # Calcular direção (N, NE, E, etc)
        dx = pos[0] - local_pos[0]
        dy = pos[1] - local_pos[1]
        angle = math.degrees(math.atan2(dy, dx))
        angle = (angle + 360) % 360
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        index = round(angle / 45) % 8
        print(f"   Direção: {directions[index]}")

def monitor_players():
    """Monitora as posições dos jogadores em tempo real"""
    print("Monitorando posições dos jogadores. Pressione Ctrl+C para sair.")
    try:
        while True:
            print("\n" + "="*50)
            print(f"Timestamp: {time.strftime('%H:%M:%S')}")
            show_player_positions()
            time.sleep(2)  # Atualiza a cada 2 segundos
    except KeyboardInterrupt:
        print("\nMonitoramento encerrado.")

if __name__ == "__main__":
    print("1. Mostrar posições uma vez")
    print("2. Monitorar posições em tempo real")
    print("3. Encontrar jogador pelo nome")
    choice = input("Escolha uma opção (1-3): ")
    
    if choice == "2":
        monitor_players()
    elif choice == "3":
        name = input("Digite o nome do jogador: ")
        find_player_by_name(name)
    else:
        show_player_positions()
