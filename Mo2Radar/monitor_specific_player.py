#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets
import time
import os

def monitor_specific_player(player_addr):
    mem = Reader("GameThread")
    
    # Converter o endereço de string para inteiro se necessário
    if isinstance(player_addr, str):
        player_addr = int(player_addr, 16)
    
    print(f"Monitorando jogador no endereço: 0x{player_addr:X}")
    
    # Tentar ler o nome do jogador
    try:
        name_addr, name_length = mem.read(player_addr + offsets.CreatureName, "QB")
        if name_addr > 0x10000000 and 0 < name_length < 50:
            name_bytes = max(0, name_length * 2 - 2)
            name = mem.read_string(name_addr, name_bytes, encoding="utf-16")
            print(f"Nome do jogador: {name}")
    except:
        print("Não foi possível ler o nome do jogador")
    
    # Testar diferentes offsets para RootComponent
    root_offsets = [0x1A0,0x1B8]
    pos_offsets = [0xE0, 0xF8]
    
    # Encontrar combinações válidas
    valid_combinations = []
    
    for root_offset in root_offsets:
        root_component = mem.read(player_addr + root_offset, "Q")
        if not root_component or root_component < 0x10000000:
            continue
            
        for pos_offset in pos_offsets:
            try:
                # Testar como float64
                pos = mem.read(root_component + pos_offset, "3d")
                if all(-1000000 < p < 1000000 for p in pos) and any(p != 0 for p in pos):
                    valid_combinations.append((root_offset, pos_offset, "3d"))
            except:
                pass
                
            try:
                # Testar como float32
                pos = mem.read(root_component + pos_offset, "3f")
                if all(-1000000 < p < 1000000 for p in pos) and any(p != 0 for p in pos):
                    valid_combinations.append((root_offset, pos_offset, "3f"))
            except:
                pass
    
    if not valid_combinations:
        print("Não foi possível encontrar combinações válidas para leitura de posição")
        return
    
    print(f"Encontradas {len(valid_combinations)} combinações válidas:")
    for i, (root_offset, pos_offset, format_str) in enumerate(valid_combinations):
        print(f"{i+1}. RootComponent=0x{root_offset:X}, RootPos=0x{pos_offset:X}, Format={format_str}")
    
    choice = 0
    if len(valid_combinations) > 1:
        choice = int(input(f"Escolha uma combinação (1-{len(valid_combinations)}): ")) - 1
        if choice < 0 or choice >= len(valid_combinations):
            choice = 0
    
    root_offset, pos_offset, format_str = valid_combinations[choice]
    print(f"\nMonitorando com: RootComponent=0x{root_offset:X}, RootPos=0x{pos_offset:X}, Format={format_str}")
    
    # Monitorar a posição em tempo real
    try:
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            print(f"Monitorando jogador no endereço: 0x{player_addr:X}")
            print(f"RootComponent=0x{root_offset:X}, RootPos=0x{pos_offset:X}, Format={format_str}")
            print("Pressione Ctrl+C para sair\n")
            
            try:
                root_component = mem.read(player_addr + root_offset, "Q")
                if root_component and root_component > 0x10000000:
                    pos = mem.read(root_component + pos_offset, format_str)
                    print(f"Posição: {pos}")
                    
                    # Tentar ler outros dados do jogador
                    try:
                        health = mem.read(player_addr + offsets.Health, "2f")
                        print(f"Vida: {health[0]}/{health[1]}")
                    except:
                        pass
                    
                    try:
                        is_ghost = mem.read(player_addr + offsets.IsGhost, "?")
                        print(f"É fantasma: {is_ghost}")
                    except:
                        pass
                else:
                    print("RootComponent inválido ou jogador não está mais disponível")
            except Exception as e:
                print(f"Erro ao ler dados: {e}")
            
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nMonitoramento encerrado")
    
    # Perguntar se deseja atualizar os offsets
    update = input("\nAtualizar offsets.py com estes valores? (s/n): ").lower() == 's'
    if update:
        with open("lib/offsets.py", "r") as f:
            content = f.read()
        
        content = content.replace(
            f"RootComponent = 0x{offsets.RootComponent:X}",
            f"RootComponent = 0x{root_offset:X}"
        )
        content = content.replace(
            f"RootPos = 0x{offsets.RootPos:X}",
            f"RootPos = 0x{pos_offset:X}"
        )
        
        with open("lib/offsets.py", "w") as f:
            f.write(content)
        
        # Atualizar o formato de leitura na classe Actor se necessário
        if format_str != "3d":
            with open("lib/actors.py", "r") as f:
                actor_content = f.read()
            
            old_code = 'self.pos = self.mem.read(self.root_component + offsets.RootPos, "3d")'
            new_code = f'self.pos = self.mem.read(self.root_component + offsets.RootPos, "{format_str}")'
            
            if old_code in actor_content:
                actor_content = actor_content.replace(old_code, new_code)
                
                with open("lib/actors.py", "w") as f:
                    f.write(actor_content)
        
        print("Offsets atualizados!")

if __name__ == "__main__":
    player_addr = input("Digite o endereço do jogador (ex: 0x1AB94AAB0): ")
    if not player_addr:
        player_addr = "0x1AB94AAB0"  # Usar o endereço fornecido como padrão
    
    monitor_specific_player(player_addr)