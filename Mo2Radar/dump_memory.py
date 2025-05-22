#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets
import struct
import os

def dump_memory():
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
    
    print(f"Local Pawn: 0x{local_pawn:X}")
    
    # Obter o RootComponent do jogador local
    local_root = mem.read(local_pawn + offsets.RootComponent, "Q")
    print(f"Local RootComponent: 0x{local_root:X}")
    
    # Ler um bloco maior de memória para análise
    if local_root and local_root > 0x10000000:
        try:
            # Ler 512 bytes a partir do RootComponent
            raw_data = mem.read(local_root, "512s")
            
            # Garantir que temos bytes válidos
            if raw_data is None or not isinstance(raw_data, bytes):
                raise ValueError("Falha ao ler memória: dados inválidos")
                
            print("\nDump de memória do RootComponent:")
            for i in range(0, len(raw_data), 16):
                chunk = raw_data[i:i+16]
                hex_values = ' '.join(f"{b:02X}" for b in chunk)
                ascii_values = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
                print(f"0x{i:04X}: {hex_values} | {ascii_values}")
                
                # Tentar interpretar como float64 (double)
                if i % 8 == 0 and i + 24 <= len(raw_data):
                    try:
                        values = struct.unpack("3d", raw_data[i:i+24])
                        if all(-1000000 < v < 1000000 for v in values) and any(v != 0 for v in values):
                            print(f"  Possível posição (float64) em offset 0x{i:X}: {values}")
                    except Exception as e:
                        pass
                
                # Tentar interpretar como float32 (float)
                if i % 4 == 0 and i + 12 <= len(raw_data):
                    try:
                        values = struct.unpack("3f", raw_data[i:i+12])
                        if all(-1000000 < v < 1000000 for v in values) and any(v != 0 for v in values):
                            print(f"  Possível posição (float32) em offset 0x{i:X}: {values}")
                    except Exception as e:
                        pass
        except Exception as e:
            print(f"Erro ao ler memória: {e}")
    
    # Encontrar jogadores
    print("\nProcurando jogadores:")
    
    actor_array, actor_count = mem.read(persistent_level + offsets.ActorArray, "QI")
    
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
                if len(players) >= 3:
                    break
        except:
            continue
    
    # Analisar a memória de alguns jogadores
    for actor, name in players:
        print(f"\nJogador: {name} (0x{actor:X})")
        
        # Testar diferentes offsets para RootComponent
        for root_offset in [0x188, 0x190, 0x198, 0x1A0, 0x1A8, 0x1B0, 0x1B8, 0x1C0]:
            try:
                root = mem.read(actor + root_offset, "Q")
                if root and root > 0x10000000:
                    print(f"  RootComponent em 0x{root_offset:X}: 0x{root:X}")
                    
                    # Ler um bloco de memória para análise
                    try:
                        # Ler 256 bytes a partir do RootComponent
                        raw_data = mem.read(root, "256s")
                        
                        # Garantir que temos bytes válidos
                        if raw_data is None or not isinstance(raw_data, bytes):
                            continue
                        
                        # Procurar por possíveis posições
                        for i in range(0, len(raw_data), 8):
                            # Tentar interpretar como float64 (double)
                            if i + 24 <= len(raw_data):
                                try:
                                    values = struct.unpack("3d", raw_data[i:i+24])
                                    if all(-1000000 < v < 1000000 for v in values) and any(v != 0 for v in values):
                                        print(f"    Possível posição (float64) em offset 0x{i:X}: {values}")
                                except Exception as e:
                                    pass
                            
                            # Tentar interpretar como float32 (float)
                            if i + 12 <= len(raw_data):
                                try:
                                    values = struct.unpack("3f", raw_data[i:i+12])
                                    if all(-1000000 < v < 1000000 for v in values) and any(v != 0 for v in values):
                                        print(f"    Possível posição (float32) em offset 0x{i:X}: {values}")
                                except Exception as e:
                                    pass
                    except:
                        pass
            except:
                pass

if __name__ == "__main__":
    dump_memory()