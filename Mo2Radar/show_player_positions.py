#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets
import time
import math

def distance(pos1, pos2):
    """Calcula a distância entre duas posições 3D"""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(pos1, pos2)))

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
    
    # Encontrar o jogador "Pombagira" para usar como jogador local
    local_pos = (0, 0, 0)
    local_actor = None
    
    # Ler o array de atores para encontrar Pombagira
    actor_array, actor_count = mem.read(persistent_level + offsets.ActorArray, "QI")
    
    for i in range(min(actor_count, 1000)):
        actor = mem.read(actor_array + (i * 8), "Q")
        if not actor or actor < 0x10000000:
            continue
            
        try:
            # Verificar se é um jogador
            key = mem.read(actor + 0x18, "2H")
            block = key[1] * 8
            offset = key[0] * 2
            block_ptr = mem.read(offsets.GNames + block, "Q")
            name_len = mem.read(block_ptr + offset, "H") >> 6
            fname = mem.read_string(block_ptr + offset + 2, name_len)
            
            if "BP_PlayerCharacter_C" in fname:
                # Tentar ler o nome do jogador
                try:
                    name_addr, name_length = mem.read(actor + offsets.CreatureName, "QB")
                    if name_addr > 0x10000000 and 0 < name_length < 50:
                        name_bytes = max(0, name_length * 2 - 2)
                        name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
                        
                        # Se encontrarmos Pombagira, usar como jogador local
                        if name == "Pombagira":
                            local_actor = actor
                            root_component = mem.read(actor + offsets.RootComponent, "Q")
                            if root_component and root_component > 0x10000000:
                                try:
                                    pos = mem.read(root_component + offsets.RootPos, "3d")
                                    if all(-1000000 < p < 1000000 for p in pos):
                                        local_pos = pos
                                        break
                                except:
                                    pass
                except:
                    pass
        except:
            continue
    
    print(f"Posição do jogador local: {local_pos}")
    
    # Já lemos o array de atores acima, agora vamos encontrar os outros jogadores
    # Resetar a lista de jogadores
    players = []
    
    for i in range(min(actor_count, 1000)):
        actor = mem.read(actor_array + (i * 8), "Q")
        if not actor or actor == local_actor or actor < 0x10000000:
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
    choice = input("Escolha uma opção (1-2): ")
    
    if choice == "2":
        monitor_players()
    else:
        show_player_positions()