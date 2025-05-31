import os
import time
from lib.memory import Reader
from lib import offsets
from lib.common import config
from lib.actors import Actor, Player, NPC, Mesh
from lib.graphics import PlayerBlip, NPCBlip, GenericBlip, make_view_matrix


class GameHandler:
    """tracks game state information and actors of interest"""

    __slots__ = "mem", "actor_cache", "fname_cache", "objects", "local", "tracked_players"
    
    # Configuração manual da rotação do radar
    radar_rotation = 0  # Ângulo em graus (0-360)
    radar_pitch = 0     # Inclinação vertical (-90 a 90)
    radar_fov = 90      # Campo de visão (30-120)

    def __init__(self):
        self.mem = Reader("GameThread")
        # use a set for fast membership testing
        self.actor_cache = frozenset()
        self.fname_cache = {}
        self.objects = []
        self.local = {}
        # Conjunto para rastrear jogadores já detectados
        self.tracked_players = set()
    
    def set_radar_rotation(self, angle):
        """Define a rotação manual do radar (ângulo em graus)"""
        self.__class__.radar_rotation = angle % 360
        print(f"Rotação do radar definida para {self.__class__.radar_rotation}°")
    
    def adjust_radar_rotation(self, delta):
        """Ajusta a rotação do radar em incrementos (delta em graus)"""
        self.__class__.radar_rotation = (self.__class__.radar_rotation + delta) % 360
        print(f"Rotação do radar ajustada para {self.__class__.radar_rotation}°")
    
    def set_radar_pitch(self, angle):
        """Define a inclinação vertical do radar (ângulo em graus)"""
        self.__class__.radar_pitch = max(-90, min(90, angle))
        print(f"Inclinação do radar definida para {self.__class__.radar_pitch}°")
    
    def set_radar_fov(self, fov):
        """Define o campo de visão do radar"""
        self.__class__.radar_fov = max(30, min(120, fov))
        print(f"FOV do radar definido para {self.__class__.radar_fov}°")

    def update_local(self, uworld: int):
        """Update local player position, view matrix, and pawn address"""
        # UWorld->OwningGameInstance->*LocalPlayer->PlayerController
        game_instance = self.mem.read(uworld + offsets.OwningGameInstance, "Q")
        local_players = self.mem.read(game_instance + offsets.LocalPlayers, "Q")
        local_player = self.mem.read(local_players, "Q")  # local_players[0]
        controller = self.mem.read(local_player + offsets.PlayerController, "Q")

        # PlayerController->AcknowledgedPawn
        pawn = self.mem.read(controller + offsets.AcknowledgedPawn, "Q")
        self.local["pawn"] = pawn
        
        # Obter a posição diretamente do pawn
        if pawn:
            root_component = self.mem.read(pawn + offsets.RootComponent, "Q")
            if root_component:
                # Lê a posição do jogador
                self.local["pos"] = self.mem.read(root_component + offsets.RootPos, "3d")
                
                # Usa a rotação manual configurada
                view = [
                    self.__class__.radar_pitch,  # pitch
                    self.__class__.radar_rotation,  # yaw
                    0,  # roll
                    self.__class__.radar_fov  # FOV
                ]
                self.local["view_matrix"] = make_view_matrix(self.local["pos"], view)
        else:
            # Valores padrão se não conseguir ler o pawn
            self.local["pos"] = (0, 0, 0)
            self.local["view_matrix"] = make_view_matrix((0, 0, 0), [0, 0, 0, 90])

    
    def get_fname(self, key: tuple[int, int]) -> str:
        """Return a key's FName value"""
        try:
            # use cached value if possible
            return self.fname_cache[key]
        except KeyError:
            # retrieve fname from string intern pool using its key
            # see UnrealNames.cpp and NameTypes.h

            # FNameEntryHandle
            block = key[1] * 8
            offset = key[0] * 2

            block_ptr = self.mem.read(offsets.GNames + block, "Q")

            # FNameEntryHeader
            name_len = self.mem.read(block_ptr + offset, "H") >> 6
            name = self.mem.read_string(block_ptr + offset + 2, name_len)

            self.fname_cache[key] = name  # cache it for later
            # you can use the debug_fnames option to find actor fnames
            # consider outputting the program to a file, e.g.:
            # sudo python -OO main.py > fname_dump.txt
            # and then you can search it later.
            if config["debug_fnames"]:
                print(name)
            return name

    def read_actors(self, uworld: int) -> tuple[int, str]:
        """
        Read actor array, read fnames of new actors,
        update actor cache, return list of new actors.
        """
        persistent_level = self.mem.read(uworld + offsets.PersistentLevel, "Q")
        # UWorld->PersistentLevel->ActorArray, PersistentLevel.ActorCount
        actor_array, actor_count = self.mem.read(
            persistent_level + offsets.ActorArray, "QH"
        )

        current_actors = frozenset(self.mem.read(actor_array, str(actor_count) + "Q"))

        new_actors = []
        # loop through addresses that are in current_actors
        # but not in self.actor_cache
        for addr in current_actors - self.actor_cache:
            if not addr:
                continue
            # I like bitmath but reading the key as two uint16s is simpler
            key = self.mem.read(addr + 0x18, "2H")
            fname = self.get_fname(key)
            new_actors.append((addr, fname))

        # replace cache with the most recent actor array
        self.actor_cache = current_actors
        return new_actors

    def init_actor(self, addr: int, fname: str):
        """Parse an actor's fname and add a blip to self.objects if it matches"""
        # I don't like the way I designed the config file but I'm too lazy to change it.

        if fname.startswith("BP_PlayerCharacter_") and addr != self.local["pawn"]:
            actor = Player(addr, fname, self.mem)
            blip = PlayerBlip(actor)
            self.objects.append(blip)
            
            # Verificar se é um novo jogador e emitir um bip
            if addr not in self.tracked_players:
                print("\a")  # Emite um bip sonoro
                self.tracked_players.add(addr)
            return

        is_npc = any(fname.startswith(prefix) for prefix in config["npc_prefixes"])
        if config.get("show_npcs", True) and is_npc and any(npc in fname for npc in config["npc"]):
            actor = NPC(addr, fname, self.mem)
            blip = NPCBlip(actor)
            self.objects.append(blip)
            return

        if any(mesh in fname for mesh in config["mesh"]):
            actor = Mesh(addr, fname, self.mem)
            blip = GenericBlip(actor)
            self.objects.append(blip)
            return

        if config["debug_actors"]:
            actor = Actor(addr, fname, self.mem)
            blip = GenericBlip(actor)
            self.objects.append(blip)            
            return

    def update_objects(self, tries=0):
        try:
            uworld = self.mem.read(offsets.GWorld, "Q")
            self.update_local(uworld)
            new_actors = self.read_actors(uworld)

        except TypeError as e:
            # changing levels or the process died.

            # signal 0 doesn't actually send a signal,
            # it just checks if the process is alive.
            os.kill(self.mem.pid, 0)
            if tries > 300:  # 30s
                raise RuntimeError("Bad offsets or game is stalled!") from e
            time.sleep(0.1)
            self.update_objects(tries + 1)
            return

        # Limpar jogadores que não estão mais no radar
        current_actors_set = set(addr for addr, _ in new_actors)
        removed_players = self.tracked_players - current_actors_set
        for addr in removed_players:
            self.tracked_players.remove(addr)

        for addr, fname in new_actors:
            self.init_actor(addr, fname)

        # use a copy since we're modifying the original list
        for obj in self.objects.copy():
            is_loaded = obj.actor.addr in self.actor_cache
            is_local_player = obj.actor.addr == self.local["pawn"]
            if is_loaded and not is_local_player:
                try:
                    obj.update(self.local["pos"], self.local["view_matrix"])
                    continue
                except TypeError:
                    # the actor either just unloaded
                    # or was never a valid actor to begin with.
                    pass
            obj.delete()
            self.objects.remove(obj)