#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets
import time
import math

def distance(pos1, pos2):
    """Calcula a distância entre duas posições 3D"""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(pos1, pos2)))

def test_actor_positions():
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
    
    # Obter o jogador local para referência
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
    
    print(f"Total de atores: {actor_count}")
    
    # Encontrar atores de jogadores e NPCs
    players = []
    npcs = []
    
    for i in range(min(actor_count, 500)):  # Limitar a 500 atores para evitar lentidão
        actor = mem.read(actor_array + (i * 8), "Q")
        if not actor or actor == local_pawn or actor < 0x10000000:
            continue
            
        try:
            # Ler o FName key para identificar o tipo de ator
            key = mem.read(actor + 0x18, "2H")
            
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
            
            # Tentar ler o nome (se disponível)
            name = "Desconhecido"
            try:
                name_addr, name_length = mem.read(actor + offsets.CreatureName, "QB")
                if name_addr > 0x10000000 and name_length < 50:
                    name_bytes = max(0, name_length * 2 - 2)
                    name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
            except:
                pass
                
            # Classificar como jogador ou NPC com base no nome ou tipo
            if "BP_PlayerCharacter_" in str(key):
                players.append((actor, name, pos, dist))
            elif any(prefix in str(key) for prefix in ["BP_NPC_", "BP_Creature_"]):
                npcs.append((actor, name, pos, dist))
        except:
            continue
    
    # Mostrar jogadores encontrados (ordenados por distância)
    print("\n=== JOGADORES ENCONTRADOS ===")
    for i, (addr, name, pos, dist) in enumerate(sorted(players, key=lambda x: x[3])):
        print(f"{i+1}. {name} (0x{addr:X})")
        print(f"   Posição: {pos}")
        print(f"   Distância: {dist:.1f}")
        print(f"   Direção: {calculate_direction(local_pos, pos)}")
        
    # Mostrar NPCs encontrados (ordenados por distância)
    print("\n=== NPCs ENCONTRADOS ===")
    for i, (addr, name, pos, dist) in enumerate(sorted(npcs, key=lambda x: x[3])):
        print(f"{i+1}. {name} (0x{addr:X})")
        print(f"   Posição: {pos}")
        print(f"   Distância: {dist:.1f}")
        print(f"   Direção: {calculate_direction(local_pos, pos)}")

def calculate_direction(from_pos, to_pos):
    """Calcula a direção (N, NE, E, etc) de um ponto para outro"""
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    
    angle = math.degrees(math.atan2(dy, dx))
    
    # Converter para 0-360
    angle = (angle + 360) % 360
    
    # Converter para direção
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(angle / 45) % 8
    
    return directions[index]

def monitor_positions():
    """Monitora as posições dos atores em tempo real"""
    print("Monitorando posições dos atores. Pressione Ctrl+C para sair.")
    try:
        while True:
            print("\n" + "="*50)
            print(f"Timestamp: {time.strftime('%H:%M:%S')}")
            test_actor_positions()
            time.sleep(2)  # Atualiza a cada 2 segundos
    except KeyboardInterrupt:
        print("\nMonitoramento encerrado.")

if __name__ == "__main__":
    print("1. Testar posições uma vez")
    print("2. Monitorar posições em tempo real")
    choice = input("Escolha uma opção (1-2): ")
    
    if choice == "2":
        monitor_positions()
    else:
        test_actor_positions()