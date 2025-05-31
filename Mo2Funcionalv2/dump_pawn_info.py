#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets
import time
import struct
import os

def dump_pawn_info():
    """Extrai todas as informações possíveis do pawn do jogador"""
    print("Extraindo informações do pawn do jogador...")
    mem = Reader("GameThread")
    
    # Lê o endereço base do UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    
    # Segue a cadeia para obter o pawn
    game_instance = mem.read(uworld + offsets.OwningGameInstance, "Q")
    local_players = mem.read(game_instance + offsets.LocalPlayers, "Q")
    local_player = mem.read(local_players, "Q")
    controller = mem.read(local_player + offsets.PlayerController, "Q")
    pawn = mem.read(controller + offsets.AcknowledgedPawn, "Q")
    
    if not pawn or pawn < 0x10000000:
        print("Não foi possível obter um endereço válido para o pawn.")
        return
    
    print(f"Pawn encontrado: 0x{pawn:X}")
    
    # Criar diretório para salvar o dump
    os.makedirs("dumps", exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"dumps/pawn_dump_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write(f"=== DUMP DO PAWN: 0x{pawn:X} ===\n")
        f.write(f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Informações básicas conhecidas
        try:
            # Nome do jogador
            name_addr, name_length = mem.read(pawn + offsets.CreatureName, "QB")
            if name_addr > 0x10000000 and 0 < name_length < 50:
                name_bytes = max(0, name_length * 2 - 2)
                name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
                f.write(f"Nome do jogador: {name}\n")
                print(f"Nome do jogador: {name}")
        except Exception as e:
            f.write(f"Erro ao ler o nome do jogador: {str(e)}\n")
        
        try:
            # Saúde do jogador
            health = mem.read(pawn + offsets.Health, "2f")
            f.write(f"Saúde: {health[0]}/{health[1]}\n")
            print(f"Saúde: {health[0]}/{health[1]}")
        except Exception as e:
            f.write(f"Erro ao ler a saúde: {str(e)}\n")
        
        try:
            # Posição do jogador
            root_component = mem.read(pawn + offsets.RootComponent, "Q")
            if root_component:
                pos = mem.read(root_component + offsets.RootPos, "3d")
                f.write(f"Posição: X={pos[0]:.2f}, Y={pos[1]:.2f}, Z={pos[2]:.2f}\n")
                print(f"Posição: X={pos[0]:.2f}, Y={pos[1]:.2f}, Z={pos[2]:.2f}")
        except Exception as e:
            f.write(f"Erro ao ler a posição: {str(e)}\n")
        
        # Dump de todos os offsets possíveis
        f.write("\n=== DUMP DE TODOS OS OFFSETS ===\n")
        f.write("Offset\tTipo\tValor\n")
        f.write("-" * 60 + "\n")
        
        # Escanear uma faixa grande de offsets
        for offset in range(0x0, 0x1000, 0x8):
            try:
                # Tentar ler como ponteiro
                ptr = mem.read(pawn + offset, "Q")
                if 0x10000000 < ptr < 0x7FFFFFFFFFFF:
                    f.write(f"0x{offset:04X}\tPtr\t0x{ptr:X}\n")
                    
                    # Tentar ler strings a partir do ponteiro
                    try:
                        # FString (primeiro int é comprimento)
                        str_len = mem.read(ptr, "I")
                        if 1 <= str_len <= 100:
                            string_value = mem.read_string(ptr + 4, str_len)
                            if string_value and len(string_value) >= 2 and all(32 <= ord(c) < 127 for c in string_value):
                                f.write(f"0x{offset:04X}\tFString\t{string_value}\n")
                    except:
                        pass
                    
                    # String com prefixo de comprimento de byte
                    try:
                        str_len = mem.read(ptr, "B")
                        if 1 <= str_len <= 100:
                            string_value = mem.read_string(ptr + 2, str_len)
                            if string_value and len(string_value) >= 2 and all(32 <= ord(c) < 127 for c in string_value):
                                f.write(f"0x{offset:04X}\tBStr\t{string_value}\n")
                    except:
                        pass
                    
                    # String UTF-16
                    try:
                        str_len = mem.read(ptr, "B")
                        if 1 <= str_len <= 100:
                            name_bytes = max(0, str_len * 2 - 2)
                            string_value = mem.read_string(ptr, name_bytes, encoding="utf-16")
                            if string_value and len(string_value) >= 2:
                                f.write(f"0x{offset:04X}\tUTF16\t{string_value}\n")
                    except:
                        pass
                
                # Tentar ler como int32
                int_val = mem.read(pawn + offset, "i")
                if -10000000 < int_val < 10000000:
                    f.write(f"0x{offset:04X}\tInt32\t{int_val}\n")
                
                # Tentar ler como float
                float_val = mem.read(pawn + offset, "f")
                if -1000000 < float_val < 1000000:
                    f.write(f"0x{offset:04X}\tFloat\t{float_val:.2f}\n")
                
                # Tentar ler como byte/bool
                byte_val = mem.read(pawn + offset, "B")
                if byte_val in (0, 1):
                    f.write(f"0x{offset:04X}\tBool\t{bool(byte_val)}\n")
                
            except Exception as e:
                pass
    
    print(f"\nDump completo salvo em: {filename}")
    print("Examine o arquivo para encontrar informações como nome da guilda, status, etc.")

if __name__ == "__main__":
    dump_pawn_info()