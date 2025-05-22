#!/usr/bin/env python3
from lib.memory import Reader
from lib import offsets

def test_all_offsets():
    mem = Reader("GameThread")
    
    # Obter o UWorld
    uworld = mem.read(offsets.GWorld, "Q")
    persistent_level = mem.read(uworld + offsets.PersistentLevel, "Q")
    
    print(f"UWorld: 0x{uworld:X}")
    print(f"PersistentLevel: 0x{persistent_level:X}")
    
    # Testar diferentes offsets para ActorArray
    actor_array_offsets = {}
    for offset in [0x98, 0xA0, 0xA8, 0xB0, 0xB8, 0xC0, 0xC8]:
        try:
            actor_array, actor_count = mem.read(persistent_level + offset, "QI")
            if actor_array > 0x10000000 and 0 < actor_count < 10000:
                actor_array_offsets[offset] = (actor_array, actor_count)
        except:
            pass
    
    if not actor_array_offsets:
        print("Não foi possível encontrar um offset válido para ActorArray")
        return
    
    print("\nPossíveis offsets para ActorArray:")
    for offset, (array, count) in actor_array_offsets.items():
        print(f"0x{offset:X}: Array=0x{array:X}, Count={count}")
    
    # Escolher o offset para ActorArray
    if len(actor_array_offsets) == 1:
        actor_array_offset = list(actor_array_offsets.keys())[0]
    else:
        print("\nEscolha um offset para ActorArray:")
        for i, offset in enumerate(actor_array_offsets.keys()):
            print(f"{i+1}. 0x{offset:X}")
        
        choice = int(input("\nDigite o número da opção: ")) - 1
        actor_array_offset = list(actor_array_offsets.keys())[choice]
    
    actor_array, actor_count = actor_array_offsets[actor_array_offset]
    
    # Obter o jogador local
    game_instance = mem.read(uworld + offsets.OwningGameInstance, "Q")
    local_players = mem.read(game_instance + offsets.LocalPlayers, "Q")
    local_player = mem.read(local_players, "Q")
    controller = mem.read(local_player + offsets.PlayerController, "Q")
    local_pawn = mem.read(controller + offsets.AcknowledgedPawn, "Q")
    
    print(f"\nLocal Pawn: 0x{local_pawn:X}")
    
    # Encontrar jogadores
    players = []
    for i in range(min(actor_count, 1000)):
        try:
            actor = mem.read(actor_array + (i * 8), "Q")
            if not actor or actor == local_pawn or actor < 0x10000000:
                continue
                
            # Verificar se é um jogador
            key = mem.read(actor + 0x18, "2H")
            block = key[1] * 8
            key_offset = key[0] * 2
            block_ptr = mem.read(offsets.GNames + block, "Q")
            name_len = mem.read(block_ptr + key_offset, "H") >> 6
            fname = mem.read_string(block_ptr + key_offset + 2, name_len)
            
            if "BP_PlayerCharacter_C" in fname:
                players.append(actor)
                if len(players) >= 5:
                    break
        except:
            continue
    
    if not players:
        print("\nNão foi possível encontrar jogadores")
        return
    
    print(f"\nEncontrados {len(players)} jogadores")
    
    # Testar diferentes offsets para RootComponent
    root_component_offsets = {}
    for player in players:
        for offset in [0x188, 0x190, 0x198, 0x1A0, 0x1A8, 0x1B0, 0x1B8, 0x1C0]:
            try:
                root = mem.read(player + offset, "Q")
                if root and root > 0x10000000:
                    if offset not in root_component_offsets:
                        root_component_offsets[offset] = []
                    root_component_offsets[offset].append((player, root))
            except:
                pass
    
    if not root_component_offsets:
        print("Não foi possível encontrar um offset válido para RootComponent")
        return
    
    print("\nPossíveis offsets para RootComponent:")
    for offset, roots in root_component_offsets.items():
        print(f"0x{offset:X}: {len(roots)} jogadores válidos")
    
    # Escolher o offset para RootComponent
    if len(root_component_offsets) == 1:
        root_component_offset = list(root_component_offsets.keys())[0]
    else:
        print("\nEscolha um offset para RootComponent:")
        for i, offset in enumerate(root_component_offsets.keys()):
            print(f"{i+1}. 0x{offset:X}")
        
        choice = int(input("\nDigite o número da opção: ")) - 1
        root_component_offset = list(root_component_offsets.keys())[choice]
    
    # Testar diferentes offsets para RootPos
    root_pos_offsets = {}
    for player, root in root_component_offsets[root_component_offset]:
        for offset in [0xE0, 0xE8, 0xF0, 0xF8, 0x100, 0x108, 0x110, 0x118]:
            try:
                # Testar como float64
                pos = mem.read(root + offset, "3d")
                if all(-1000000 < p < 1000000 for p in pos) and any(p != 0 for p in pos):
                    if offset not in root_pos_offsets:
                        root_pos_offsets[offset] = []
                    root_pos_offsets[offset].append((player, root, pos, "3d"))
            except:
                pass
            
            try:
                # Testar como float32
                pos = mem.read(root + offset, "3f")
                if all(-1000000 < p < 1000000 for p in pos) and any(p != 0 for p in pos):
                    if offset not in root_pos_offsets:
                        root_pos_offsets[offset] = []
                    root_pos_offsets[offset].append((player, root, pos, "3f"))
            except:
                pass
    
    if not root_pos_offsets:
        print("Não foi possível encontrar um offset válido para RootPos")
        return
    
    print("\nPossíveis offsets para RootPos:")
    for offset, positions in root_pos_offsets.items():
        print(f"0x{offset:X}: {len(positions)} posições válidas")
        for _, _, pos, format_str in positions[:2]:  # Mostrar apenas as 2 primeiras posições
            print(f"  {pos} ({format_str})")
    
    # Escolher o offset para RootPos
    if len(root_pos_offsets) == 1:
        root_pos_offset = list(root_pos_offsets.keys())[0]
        format_str = root_pos_offsets[root_pos_offset][0][3]
    else:
        print("\nEscolha um offset para RootPos:")
        for i, offset in enumerate(root_pos_offsets.keys()):
            print(f"{i+1}. 0x{offset:X}")
        
        choice = int(input("\nDigite o número da opção: ")) - 1
        root_pos_offset = list(root_pos_offsets.keys())[choice]
        
        # Determinar o formato
        formats = set(item[3] for item in root_pos_offsets[root_pos_offset])
        if len(formats) == 1:
            format_str = formats.pop()
        else:
            print("\nEscolha um formato de leitura:")
            print("1. float64 (3d)")
            print("2. float32 (3f)")
            format_choice = input("\nDigite o número da opção: ")
            format_str = "3d" if format_choice != "2" else "3f"
    
    # Atualizar os offsets
    print("\nOffsets encontrados:")
    print(f"ActorArray = 0x{actor_array_offset:X}")
    print(f"RootComponent = 0x{root_component_offset:X}")
    print(f"RootPos = 0x{root_pos_offset:X}")
    print(f"Formato = {format_str}")
    
    update = input("\nAtualizar offsets.py com estes valores? (s/n): ").lower() == 's'
    if update:
        with open("lib/offsets.py", "r") as f:
            content = f.read()
        
        content = content.replace(
            f"ActorArray = 0x{offsets.ActorArray:X}",
            f"ActorArray = 0x{actor_array_offset:X}"
        )
        content = content.replace(
            f"RootComponent = 0x{offsets.RootComponent:X}",
            f"RootComponent = 0x{root_component_offset:X}"
        )
        content = content.replace(
            f"RootPos = 0x{offsets.RootPos:X}",
            f"RootPos = 0x{root_pos_offset:X}"
        )
        
        with open("lib/offsets.py", "w") as f:
            f.write(content)
        
        # Atualizar o formato de leitura em actors.py se necessário
        if format_str != "3d":
            with open("lib/actors.py", "r") as f:
                actor_content = f.read()
            
            if '"3d"' in actor_content:
                actor_content = actor_content.replace('"3d"', '"3f"')
                
                with open("lib/actors.py", "w") as f:
                    f.write(actor_content)
        
        print("Offsets atualizados com sucesso!")

if __name__ == "__main__":
    test_all_offsets()