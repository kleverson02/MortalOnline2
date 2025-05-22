#!/usr/bin/env python3
"""
Script para atualizar manualmente os offsets no arquivo offsets.py
"""
import os
import re

def update_offset(offset_name, new_value):
    """
    Atualiza um offset específico no arquivo offsets.py
    
    Args:
        offset_name: Nome do offset a ser atualizado
        new_value: Novo valor do offset (em formato hexadecimal, ex: "0xB8")
    
    Returns:
        True se o offset foi atualizado com sucesso, False caso contrário
    """
    # Verifica se o valor está no formato correto
    if not re.match(r'^0x[0-9A-Fa-f]+$', new_value):
        print(f"Erro: O valor '{new_value}' não está no formato hexadecimal correto (ex: 0xB8)")
        return False
    
    # Caminho para o arquivo offsets.py
    offsets_file = "lib/offsets.py"
    
    # Verifica se o arquivo existe
    if not os.path.exists(offsets_file):
        print(f"Erro: O arquivo {offsets_file} não foi encontrado")
        return False
    
    try:
        # Lê o conteúdo do arquivo
        with open(offsets_file, "r") as f:
            content = f.read()
        
        # Procura pelo padrão do offset
        pattern = rf"{offset_name} = 0x[0-9A-Fa-f]+"
        match = re.search(pattern, content)
        
        if not match:
            print(f"Erro: Não foi possível encontrar o offset '{offset_name}' no arquivo")
            return False
        
        # Substitui o valor do offset
        old_value = match.group(0)
        new_line = f"{offset_name} = {new_value}"
        updated_content = content.replace(old_value, new_line)
        
        # Escreve o arquivo atualizado
        with open(offsets_file, "w") as f:
            f.write(updated_content)
        
        print(f"Offset '{offset_name}' atualizado com sucesso: {old_value.split(' = ')[1]} -> {new_value}")
        return True
        
    except Exception as e:
        print(f"Erro ao atualizar o offset: {e}")
        return False

def main():
    print("Ferramenta para atualizar offsets no arquivo offsets.py")
    print("------------------------------------------------------")
    
    while True:
        print("\nOpções:")
        print("1. Atualizar um offset")
        print("2. Sair")
        
        choice = input("\nEscolha uma opção (1-2): ")
        
        if choice == "1":
            offset_name = input("Digite o nome do offset a ser atualizado (ex: ActorArray): ")
            new_value = input("Digite o novo valor em hexadecimal (ex: 0xB8): ")
            
            update_offset(offset_name, new_value)
            
        elif choice == "2":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()