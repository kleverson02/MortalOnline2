#!/usr/bin/env python3

def update_game_py():
    with open("lib/game.py", "r") as f:
        content = f.read()
    
    # Modificar a condição para detectar jogadores
    old_code = """        if fname.startswith("BP_PlayerCharacter_") and addr != self.local["pawn"]:
            actor = Player(addr, fname, self.mem)
            blip = PlayerBlip(actor)
            self.objects.append(blip)
            return"""
    
    new_code = """        if ("BP_PlayerCharacter" in fname or "Character" in fname) and addr != self.local["pawn"]:
            actor = Player(addr, fname, self.mem)
            blip = PlayerBlip(actor)
            self.objects.append(blip)
            return"""
    
    # Verificar se o código já foi modificado
    if "BP_PlayerCharacter_C" in content:
        print("O código já foi modificado anteriormente.")
        return
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        with open("lib/game.py", "w") as f:
            f.write(content)
        
        print("Código atualizado com sucesso!")
    else:
        print("Não foi possível encontrar o código para atualizar.")

if __name__ == "__main__":
    update_game_py()