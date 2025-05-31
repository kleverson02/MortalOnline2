#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets
import time
import os

def scan_is_ghost_extended():
    """Escaneia offsets para confirmar o valor correto de isGhost com verificação estendida"""
    print("Escaneando offsets para confirmar isGhost (verificação estendida)...")
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
    filename = f"ghost_scans/is_ghost_extended_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write(f"=== SCAN ESTENDIDO DE ISGHOST NO PAWN: 0x{pawn:X} ===\n")
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
        
        # Escanear uma faixa ampla de offsets para encontrar possíveis valores booleanos
        f.write("=== ESCANEANDO POSSÍVEIS VALORES BOOLEANOS ===\n")
        f.write("Offset\tByte\tBool\tInt8\tInt16\tInt32\n")
        f.write("-" * 60 + "\n")
        
        # Escanear uma faixa ampla
        for offset in range(0x600, 0x800):
            try:
                # Ler como byte
                byte_val = mem.read(pawn + offset, "B")
                
                # Ler como booleano
                bool_val = mem.read(pawn + offset, "?")
                
                # Ler como int8
                int8_val = mem.read(pawn + offset, "b")
                
                # Ler como int16
                int16_val = mem.read(pawn + offset, "h")
                
                # Ler como int32
                int32_val = mem.read(pawn + offset, "i")
                
                # Registrar apenas valores que parecem booleanos ou flags
                if byte_val in (0, 1) or int8_val in (0, 1) or int16_val in (0, 1) or int32_val in (0, 1):
                    f.write(f"0x{offset:04X}\t{byte_val}\t{bool_val}\t{int8_val}\t{int16_val}\t{int32_val}\n")
            except:
                pass
        
        # Verificar outros jogadores para comparação
        f.write("\n=== VERIFICANDO OUTROS JOGADORES PARA COMPARAÇÃO ===\n")
        
        # Obter a lista de atores
        persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
        actor_array, actor_count = mem.read(persistent_level + offsets.ActorArray, "QH")
        
        # Escanear todos os atores
        actors = mem.read(actor_array, f"{actor_count}Q")
        player_count = 0
        
        for addr in actors:
            if not addr or addr == pawn:
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
                f.write(f"\nJogador {player_count}: 0x{addr:X}\n")
                
                # Tentar ler o nome do jogador
                try:
                    name_addr, name_length = mem.read(addr + offsets.CreatureName, "QB")
                    if name_addr > 0x10000000 and 0 < name_length < 50:
                        name_bytes = max(0, name_length * 2 - 2)
                        name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
                        f.write(f"Nome: {name}\n")
                except:
                    pass
                
                # Verificar o valor de isGhost para este jogador
                try:
                    is_ghost = mem.read(addr + offsets.IsGhost, "?")
                    f.write(f"isGhost (0x{offsets.IsGhost:X}): {is_ghost}\n")
                except:
                    f.write(f"Erro ao ler isGhost\n")
                
                # Verificar outros possíveis offsets de isGhost
                f.write("Outros possíveis valores de isGhost:\n")
                for offset in range(0x600, 0x800):
                    try:
                        byte_val = mem.read(addr + offset, "B")
                        if byte_val in (0, 1):
                            f.write(f"0x{offset:04X}: {bool(byte_val)}\n")
                    except:
                        pass
            except:
                continue
    
    print(f"\nScan estendido completo! Resultados salvos em: {filename}")
    print("\nInstruções para confirmar isGhost:")
    print("1. Execute este script quando você estiver vivo (não fantasma)")
    print("2. Anote os offsets que têm valor False")
    print("3. Morra no jogo para virar um fantasma")
    print("4. Execute o script novamente")
    print("5. Compare os resultados - o offset que mudou de False para True é o isGhost")
    print("6. Confirme verificando outros jogadores vivos e mortos")

if __name__ == "__main__":
    scan_is_ghost_extended()