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
        # Actor->Name, Actor.NameLength
        name_addr, name_length = self.mem.read(name_ptr, "QB")
        name_bytes = max(0, name_length * 2 - 2)
        name = self.mem.read_string(name_addr, name_bytes, encoding="utf-16")
        return name

    def update_actor_state(self):
        # Actor->RootComponent.RootPosition
        # UE5 is more or less the same as UE4 for our purposes,
        # but it uses float64s for coordinates instead of float32s.
        self.pos = self.mem.read(self.root_component + offsets.RootPos, "3d")


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
        self.health = self.mem.read(self.addr + offsets.Health, "2f")


class Player(NPC):
    """Player data handler"""

    __slots__ = ("is_ghost", "guild_name")

    def __init__(self, addr: int, fname: str, memory: Reader):
        super().__init__(addr, fname, memory)
        self.is_ghost = False
        self.guild_name = ""

    def update_actor_state(self):
        super().update_actor_state()
        # Actor.IsGhost
        self.is_ghost = self.mem.read(self.addr + offsets.IsGhost, "?")
        
        # Tentar ler o nome da guilda
        try:
            # Verificar se o offset GuildName está definido
            if hasattr(offsets, "GuildName"):
                # Ler o ponteiro para o nome da guilda
                guild_ptr = self.mem.read(self.addr + offsets.GuildName, "Q")
                if guild_ptr and guild_ptr > 0x10000000:
                    # Tentar ler como FString (primeiro int é comprimento)
                    str_len = self.mem.read(guild_ptr, "I")
                    if 1 <= str_len <= 50:  # Tamanho razoável
                        guild_str = self.mem.read_string(guild_ptr + 4, str_len)
                        if guild_str and len(guild_str) >= 1:
                            self.guild_name = guild_str
        except:
            self.guild_name = ""


class Mesh(Actor):
    """StaticMesh data handler"""

    def update_actor_state(self):
        super().update_actor_state()
        self.name = self.read_name(self.addr + offsets.MeshName)
