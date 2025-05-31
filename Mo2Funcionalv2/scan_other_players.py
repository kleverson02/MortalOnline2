#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets
import time
import os

def scan_other_players():
    """Escaneia informações de outros jogadores no jogo"""
    print("Escaneando informações de outros jogadores...")
    mem = Reader("GameThread")
    
    # Lê o endereço base do UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    
    # Segue a cadeia para obter o pawn local
    game_instance = mem.read(uworld + offsets.OwningGameInstance, "Q")
    local_players = mem.read(game_instance + offsets.LocalPlayers, "Q")
    local_player = mem.read(local_players, "Q")
    controller = mem.read(local_player + offsets.PlayerController, "Q")
    local_pawn = mem.read(controller + offsets.AcknowledgedPawn, "Q")
    
    if not local_pawn:
        print("Não foi possível obter o pawn local.")
        return
    
    print(f"Pawn local: 0x{local_pawn:X}")
    
    # Criar diretório para salvar o dump
    os.makedirs("player_scans", exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"player_scans/other_players_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write(f"=== SCAN DE OUTROS JOGADORES ===\n")
        f.write(f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Obter a lista de atores
        persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
        actor_array, actor_count = mem.read(persistent_level + offsets.ActorArray, "QH")
        
        f.write(f"Total de atores: {actor_count}\n\n")
        
        # Contador de jogadores encontrados
        player_count = 0
        
        # Escanear todos os atores
        actors = mem.read(actor_array, f"{actor_count}Q")
        for i, addr in enumerate(actors):
            if not addr or addr == local_pawn:
                continue
                
            try:
                # Verificar se é um jogador (BP_PlayerCharacter_)
                key = mem.read(addr + 0x18, "2H")
                block = key[1] * 8
                offset_in_block = key[0] * 2
                block_ptr = mem.read(offsets.GNames + block, "Q")
                name_len = mem.read(block_ptr + offset_in_block, "H") >> 6
                fname = mem.read_string(block_ptr + offset_in_block + 2, name_len)
                
                if not fname.startswith("BP_PlayerCharacter_"):
                    continue
                
                player_count += 1
                f.write(f"=== JOGADOR {player_count} ===\n")
                f.write(f"Endereço: 0x{addr:X}\n")
                f.write(f"FName: {fname}\n")
                
                # Tentar ler o nome do jogador
                try:
                    name_addr, name_length = mem.read(addr + offsets.CreatureName, "QB")
                    if name_addr > 0x10000000 and 0 < name_length < 50:
                        name_bytes = max(0, name_length * 2 - 2)
                        name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
                        f.write(f"Nome: {name}\n")
                except Exception as e:
                    f.write(f"Erro ao ler nome: {str(e)}\n")
                
                # Tentar ler a saúde
                try:
                    health = mem.read(addr + offsets.Health, "2f")
                    f.write(f"Saúde: {health[0]}/{health[1]}\n")
                except Exception as e:
                    f.write(f"Erro ao ler saúde: {str(e)}\n")
                
                # Tentar ler a posição
                try:
                    root_component = mem.read(addr + offsets.RootComponent, "Q")
                    if root_component:
                        pos = mem.read(root_component + offsets.RootPos, "3d")
                        f.write(f"Posição: X={pos[0]:.2f}, Y={pos[1]:.2f}, Z={pos[2]:.2f}\n")
                except Exception as e:
                    f.write(f"Erro ao ler posição: {str(e)}\n")
                
                # Escanear por possível nome de guilda
                f.write("\nPossíveis nomes de guilda:\n")
                for offset in range(0x0, 0x1000, 0x8):
                    try:
                        ptr = mem.read(addr + offset, "Q")
                        if 0x10000000 < ptr < 0x7FFFFFFFFFFF:
                            # Tentar ler como string
                            try:
                                # FString (primeiro int é comprimento)
                                str_len = mem.read(ptr, "I")
                                if 1 <= str_len <= 50:
                                    string_value = mem.read_string(ptr + 4, str_len)
                                    if string_value and len(string_value) >= 2 and all(32 <= ord(c) < 127 for c in string_value):
                                        f.write(f"  0x{offset:04X} FString: {string_value}\n")
                            except:
                                pass
                            
                            # String com prefixo de comprimento de byte
                            try:
                                str_len = mem.read(ptr, "B")
                                if 1 <= str_len <= 50:
                                    string_value = mem.read_string(ptr + 2, str_len)
                                    if string_value and len(string_value) >= 2 and all(32 <= ord(c) < 127 for c in string_value):
                                        f.write(f"  0x{offset:04X} BString: {string_value}\n")
                            except:
                                pass
                    except:
                        pass
                
                f.write("\n" + "=" * 50 + "\n\n")
                
            except Exception as e:
                continue
        
        f.write(f"\nTotal de jogadores encontrados: {player_count}\n")
    
    print(f"\nScan completo! Encontrados {player_count} jogadores.")
    print(f"Resultados salvos em: {filename}")

if __name__ == "__main__":
    scan_other_players()