#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets
import struct

def test_position_formats():
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
    
    if not local_root or local_root < 0x10000000:
        print("RootComponent inválido. Verifique o offset RootComponent.")
        return
    
    # Testar diferentes formatos de leitura para a posição
    print("\nTestando diferentes formatos de leitura para a posição:")
    
    # Ler um bloco de memória maior para análise
    try:
        mem_block = mem.read(local_root + offsets.RootPos - 16, 64)
        
        # Testar como float64 (double)
        try:
            pos_d = struct.unpack("3d", mem_block[16:40])
            print(f"Como float64 (3d): {pos_d}")
        except:
            print("Erro ao ler como float64 (3d)")
        
        # Testar como float32 (float)
        try:
            pos_f = struct.unpack("3f", mem_block[16:28])
            print(f"Como float32 (3f): {pos_f}")
        except:
            print("Erro ao ler como float32 (3f)")
        
        # Testar com offsets diferentes
        for offset in range(0, 32, 8):
            try:
                pos = struct.unpack("3d", mem_block[offset:offset+24])
                print(f"Offset +{offset}: {pos}")
            except:
                pass
    except:
        print("Erro ao ler o bloco de memória")
    
    # Encontrar jogadores
    print("\nProcurando por jogadores:")
    
    for i in range(min(100, 1000)):
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
                print(f"\nJogador encontrado: 0x{actor:X}")
                
                # Tentar ler o nome
                try:
                    name_addr, name_length = mem.read(actor + offsets.CreatureName, "QB")
                    if name_addr > 0x10000000 and 0 < name_length < 50:
                        name_bytes = max(0, name_length * 2 - 2)
                        name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
                        print(f"Nome: {name}")
                except:
                    print("Não foi possível ler o nome")
                
                # Testar diferentes offsets para RootComponent
                for root_offset in [0x188, 0x190, 0x198, 0x1A0, 0x1A8, 0x1B0, 0x1B8]:
                    root = mem.read(actor + root_offset, "Q")
                    if root and root > 0x10000000:
                        print(f"RootComponent em 0x{root_offset:X}: 0x{root:X}")
                        
                        # Testar diferentes formatos para a posição
                        for pos_offset in [0xE8, 0xF0, 0xF8, 0x100, 0x108, 0x110]:
                            try:
                                # Como float64
                                pos_d = mem.read(root + pos_offset, "3d")
                                if all(-1000000 < p < 1000000 for p in pos_d):
                                    print(f"  Posição (float64) em 0x{pos_offset:X}: {pos_d}")
                            except:
                                pass
                            
                            try:
                                # Como float32
                                pos_f = mem.read(root + pos_offset, "3f")
                                if all(-1000000 < p < 1000000 for p in pos_f):
                                    print(f"  Posição (float32) em 0x{pos_offset:X}: {pos_f}")
                            except:
                                pass
                
                break  # Encontrar apenas o primeiro jogador
        except:
            continue

if __name__ == "__main__":
    test_position_formats()