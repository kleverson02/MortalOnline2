#!/usr/bin/env python3
import os
import sys
import time
import subprocess

def run_radar():
    print("Iniciando o radar com verificações adicionais...")
    
    # Verificar se o arquivo main.py existe
    if not os.path.exists("main.py"):
        print("Erro: O arquivo main.py não foi encontrado.")
        return
    
    # Verificar se os offsets estão configurados corretamente
    from lib import offsets
    
    print("Offsets atuais:")
    print(f"ActorArray = 0x{offsets.ActorArray:X}")
    print(f"RootComponent = 0x{offsets.RootComponent:X}")
    print(f"RootPos = 0x{offsets.RootPos:X}")
    print(f"CreatureName = 0x{offsets.CreatureName:X}")
    
    # Perguntar se deseja continuar
    response = input("\nDeseja iniciar o radar com esses offsets? (s/n): ")
    if response.lower() != 's':
        print("Operação cancelada.")
        return
    
    # Iniciar o radar
    print("\nIniciando o radar...")
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\nRadar encerrado pelo usuário.")
    except Exception as e:
        print(f"\nErro ao executar o radar: {e}")

if __name__ == "__main__":
    run_radar()