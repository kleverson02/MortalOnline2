#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets
import time
import os

def scan_is_ghost():
    """Escaneia offsets para confirmar o valor correto de isGhost"""
    print("Escaneando offsets para confirmar isGhost...")
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
    print(f"Offset atual de isGhost: 0x{offsets.IsGhost:X}")
    
    # Criar diretório para salvar os resultados
    os.makedirs("ghost_scans", exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"ghost_scans/is_ghost_scan_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write(f"=== SCAN DE ISGHOST NO PAWN: 0x{pawn:X} ===\n")
        f.write(f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Offset atual de isGhost: 0x{offsets.IsGhost:X}\n\n")
        
        # Verificar o valor atual de isGhost
        try:
            current_is_ghost = mem.read(pawn + offsets.IsGhost, "?")
            f.write(f"Valor atual de isGhost: {current_is_ghost}\n\n")
            print(f"Valor atual de isGhost: {current_is_ghost}")
        except Exception as e:
            f.write(f"Erro ao ler isGhost atual: {str(e)}\n\n")
            print(f"Erro ao ler isGhost atual: {str(e)}")
        
        # Escanear uma faixa de offsets para encontrar possíveis valores booleanos
        f.write("=== ESCANEANDO POSSÍVEIS VALORES BOOLEANOS ===\n")
        f.write("Offset\tValor\n")
        f.write("-" * 30 + "\n")
        
        # Escanear uma faixa ampla ao redor do offset atual
        start_offset = max(0, offsets.IsGhost - 0x100)
        end_offset = offsets.IsGhost + 0x100
        
        for offset in range(start_offset, end_offset):
            try:
                # Tentar ler como booleano
                bool_val = mem.read(pawn + offset, "?")
                f.write(f"0x{offset:04X}\t{bool_val}\n")
            except:
                pass
    
    print(f"\nScan completo! Resultados salvos em: {filename}")
    print("\nInstruções para confirmar isGhost:")
    print("1. Execute este script quando você estiver vivo (não fantasma)")
    print("2. Anote os offsets que têm valor False")
    print("3. Morra no jogo para virar um fantasma")
    print("4. Execute o script novamente")
    print("5. Compare os resultados - o offset que mudou de False para True é o isGhost")
    print("6. Confirme atualizando o valor em lib/offsets.py")

if __name__ == "__main__":
    scan_is_ghost()