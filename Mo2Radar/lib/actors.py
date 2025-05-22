from lib.memory import Reader
from lib import offsets


class Actor:
    """Base actor data handler"""

    __slots__ = "mem", "addr", "fname", "root_component", "pos", "name"

    def __init__(self, addr: int, fname: str, memory: Reader):
        self.mem = memory
        self.addr = addr
        self.fname = fname
        self.root_component = self.mem.read(addr + offsets.RootComponent, "Q")
        self.pos = 0.0, 0.0, 0.0
        self.name = fname

    def read_name(self, name_ptr: int) -> str:
        """Read actor name from pointer and return it"""
        try:
            # Actor->Name, Actor.NameLength
            if not name_ptr or name_ptr < 0x10000000:
                return "Unknown"
            name_data = self.mem.read(name_ptr, "QB")
            if not name_data:
                return "Unknown"
            name_addr, name_length = name_data
            if not name_addr or name_addr < 0x10000000 or name_length <= 0 or name_length > 100:
                return "Unknown"
            name_bytes = max(0, name_length * 2 - 2)
            name = self.mem.read_string(name_addr, name_bytes, encoding="utf-16")
            return name if name else "Unknown"
        except:
            return "Unknown"

    def update_actor_state(self):
        # Atualizar o nome
        self.name = self.read_name(self.addr + offsets.CreatureName)
        
        # Atualizar a posição
        try:
            # Verificar se o RootComponent é válido
            if not self.root_component or self.root_component < 0x10000000:
                self.pos = (0.0, 0.0, 0.0)
                return
            
            # Testar diferentes offsets para RootPos
            for pos_offset in [offsets.RootPos, 0xE8, 0xF0, 0xF8, 0x100, 0x108, 0x110]:
                # Tentar como float32
                try:
                    pos = self.mem.read(self.root_component + pos_offset, "3f")
                    if pos and any(p != 0 for p in pos) and all(-1000000 < p < 1000000 for p in pos):
                        # Verificar se a posição mudou desde a última leitura
                        if pos != self.pos and "BP_PlayerCharacter_C" in self.fname:
                            print(f"Jogador: {self.name} | Posição em 0x{pos_offset:X} (float32): {pos}")
                        self.pos = pos
                        return
                except:
                    pass
                
                # Tentar como float64
                try:
                    pos = self.mem.read(self.root_component + pos_offset, "3d")
                    if pos and any(p != 0 for p in pos) and all(-1000000 < p < 1000000 for p in pos):
                        # Verificar se a posição mudou desde a última leitura
                        if pos != self.pos and "BP_PlayerCharacter_C" in self.fname:
                            print(f"Jogador: {self.name} | Posição em 0x{pos_offset:X} (float64): {pos}")
                        self.pos = pos
                        return
                except:
                    pass
            
            # Se chegou aqui, não conseguiu ler a posição
            self.pos = (0.0, 0.0, 0.0)
        except:
            # Fallback para coordenadas zero
            self.pos = (0.0, 0.0, 0.0)





class NPC(Actor):
    """NPC data handler"""

    __slots__ = ("health",)

    def __init__(self, addr: int, fname: str, memory: Reader):
        super().__init__(addr, fname, memory)
        self.health = 0.0, 0.0

    def update_actor_state(self):
        super().update_actor_state()
        self.name = self.read_name(self.addr + offsets.CreatureName)
        # Actor.Health, Actor.MaxHealth
        try:
            self.health = self.mem.read(self.addr + offsets.Health, "2f")
        except:
            self.health = 0.0, 0.0


class Player(NPC):
    """Player data handler"""

    __slots__ = ("is_ghost",)

    def __init__(self, addr: int, fname: str, memory: Reader):
        super().__init__(addr, fname, memory)
        self.is_ghost = False

    def update_actor_state(self):
        super().update_actor_state()
        # Actor.IsGhost
        try:
            self.is_ghost = self.mem.read(self.addr + offsets.IsGhost, "?")
        except:
            self.is_ghost = False


class Mesh(Actor):
    """StaticMesh data handler"""

    def update_actor_state(self):
        super().update_actor_state()
        self.name = self.read_name(self.addr + offsets.MeshName)