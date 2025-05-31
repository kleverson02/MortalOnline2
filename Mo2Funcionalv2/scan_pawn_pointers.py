#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets
import time
import os

def scan_pawn_pointers():
    """Escaneia os ponteiros do pawn para encontrar informações adicionais"""
    print("Escaneando ponteiros do pawn...")
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
    os.makedirs("pointer_scans", exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"pointer_scans/pawn_pointers_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write(f"=== SCAN DE PONTEIROS DO PAWN: 0x{pawn:X} ===\n")
        f.write(f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Primeiro, encontrar todos os ponteiros válidos no pawn
        pointers = []
        for offset in range(0x0, 0x1000, 0x8):
            try:
                ptr = mem.read(pawn + offset, "Q")
                if 0x10000000 < ptr < 0x7FFFFFFFFFFF:
                    pointers.append((offset, ptr))
                    f.write(f"Ponteiro em 0x{offset:04X}: 0x{ptr:X}\n")
            except:
                pass
        
        f.write(f"\nTotal de ponteiros encontrados: {len(pointers)}\n\n")
        f.write("=" * 60 + "\n\n")
        
        # Agora, escanear cada ponteiro para encontrar informações
        for offset, ptr in pointers:
            f.write(f"=== ESCANEANDO PONTEIRO: 0x{ptr:X} (offset 0x{offset:04X}) ===\n")
            
            # Tentar ler strings
            try:
                # FString (primeiro int é comprimento)
                str_len = mem.read(ptr, "I")
                if 1 <= str_len <= 100:
                    try:
                        string_value = mem.read_string(ptr + 4, str_len)
                        if string_value and len(string_value) >= 2 and all(32 <= ord(c) < 127 for c in string_value):
                            f.write(f"  FString: {string_value}\n")
                    except:
                        pass
            except:
                pass
            
            # String com prefixo de comprimento de byte
            try:
                str_len = mem.read(ptr, "B")
                if 1 <= str_len <= 100:
                    try:
                        string_value = mem.read_string(ptr + 2, str_len)
                        if string_value and len(string_value) >= 2 and all(32 <= ord(c) < 127 for c in string_value):
                            f.write(f"  BString: {string_value}\n")
                    except:
                        pass
            except:
                pass
            
            # String UTF-16
            try:
                str_len = mem.read(ptr, "B")
                if 1 <= str_len <= 100:
                    try:
                        name_bytes = max(0, str_len * 2 - 2)
                        string_value = mem.read_string(ptr, name_bytes, encoding="utf-16")
                        if string_value and len(string_value) >= 2:
                            f.write(f"  UTF16: {string_value}\n")
                    except:
                        pass
            except:
                pass
            
            # String terminada em nulo
            try:
                string_value = mem.read_string(ptr, 100)
                if string_value and len(string_value) >= 2 and all(32 <= ord(c) < 127 for c in string_value):
                    f.write(f"  CString: {string_value}\n")
            except:
                pass
            
            # Escanear os primeiros bytes do ponteiro para valores interessantes
            f.write("  Valores nos primeiros bytes:\n")
            for sub_offset in range(0x0, 0x100, 0x8):
                try:
                    # Inteiro
                    int_val = mem.read(ptr + sub_offset, "i")
                    if -10000000 < int_val < 10000000:
                        f.write(f"    +0x{sub_offset:04X} Int32: {int_val}\n")
                    
                    # Float
                    float_val = mem.read(ptr + sub_offset, "f")
                    if -1000000 < float_val < 1000000:
                        f.write(f"    +0x{sub_offset:04X} Float: {float_val:.2f}\n")
                    
                    # Ponteiro secundário
                    ptr2 = mem.read(ptr + sub_offset, "Q")
                    if 0x10000000 < ptr2 < 0x7FFFFFFFFFFF:
                        f.write(f"    +0x{sub_offset:04X} Ptr: 0x{ptr2:X}\n")
                        
                        # Tentar ler string do ponteiro secundário
                        try:
                            string_value = mem.read_string(ptr2, 50)
                            if string_value and len(string_value) >= 2 and all(32 <= ord(c) < 127 for c in string_value):
                                f.write(f"      -> String: {string_value}\n")
                        except:
                            pass
                except:
                    pass
            
            f.write("\n")
    
    print(f"\nScan de ponteiros completo! Resultados salvos em: {filename}")
    print("Examine o arquivo para encontrar informações como nome da guilda, status, etc.")

if __name__ == "__main__":
    scan_pawn_pointers()