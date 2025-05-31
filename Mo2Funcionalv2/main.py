import random
import pyglet

pyglet.options["debug_gl"] = False  # disable pyglet's debug mode
# pylint: disable=wrong-import-position
from pyglet.window import key

from lib.common import config
from lib.game import GameHandler
from lib.graphics import Radar, PlayerBlip

FPS = 30


def refresh_radar(_):
    game.update_objects()
    radar.compass.rotate_compass(game.local["view_matrix"])
    
    # Contar jogadores no radar
    player_count = sum(1 for obj in game.objects if isinstance(obj, PlayerBlip))
    
    # Mostrar apenas contagem de jogadores e status dos NPCs
    coords_text = f"Jogadores: {player_count}"
    coords_text += f"\nNPCs: {'Ativado' if config.get('show_npcs', True) else 'Desativado'}"
    
    coords.text = coords_text


if config["window_name"] == "":
    # if the window name isn't set, generate a random one.
    NAME_LEN = random.randint(6, 20)
    CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "
    random_characters = random.choices(CHARACTERS, k=NAME_LEN)
    WINDOW_NAME = "".join(random_characters)
else:
    WINDOW_NAME = config["window_name"]

window = pyglet.window.Window(
    config["window_size"],
    config["window_size"],
    caption=WINDOW_NAME,
    style="default",  # can be "transparent" if you want
)

# move window to default position
window.set_location(config["window_x"], config["window_y"])
# FPS counter
fps = pyglet.window.FPSDisplay(window)
fps.label.font_size = 10

radar = Radar()
game = GameHandler()

coords = pyglet.text.Label(
    " ",
    font_name="DejaVu Sans",
    font_size=10,
    x=4,
    y=config["window_size"] - 4,
    anchor_x="left",
    anchor_y="top",
    multiline=True,
    width=180,
    batch=Radar.BATCH,
)


@window.event
def on_draw():
    window.clear()
    Radar.BATCH.draw()
    fps.draw()

@window.event
def on_key_press(symbol, _modifiers):
    # up arrow or pageup to zoom in, down arrow or pagedown to zoom out
    match symbol:
        case key.UP | key.PAGEUP:
            Radar.RANGE = max(Radar.RANGE - 2000, 2000)
            radar.build_rings()
        case key.DOWN | key.PAGEDOWN:
            Radar.RANGE = min(Radar.RANGE + 2000, 100000)
            radar.build_rings()
        # Controles de rotação do radar
        case key.LEFT:
            game.adjust_radar_rotation(-10)
            print(f"Rotação do radar: {game.radar_rotation}°")
        case key.RIGHT:
            game.adjust_radar_rotation(10)
            print(f"Rotação do radar: {game.radar_rotation}°")
        # Controles de inclinação
        case key.W:
            game.set_radar_pitch(game.radar_pitch + 5)
            print(f"Inclinação do radar: {game.radar_pitch}°")
        case key.S:
            game.set_radar_pitch(game.radar_pitch - 5)
            print(f"Inclinação do radar: {game.radar_pitch}°")
        # Controles de FOV
        case key.A:
            game.set_radar_fov(game.radar_fov - 5)
            print(f"FOV do radar: {game.radar_fov}°")
        case key.D:
            game.set_radar_fov(game.radar_fov + 5)
            print(f"FOV do radar: {game.radar_fov}°")
        # Resetar configurações
        case key.R:
            game.set_radar_rotation(0)
            game.set_radar_pitch(0)
            game.set_radar_fov(90)
            print("Configurações do radar resetadas")
        # Alternar exibição de NPCs
        case key.N:
            config["show_npcs"] = not config.get("show_npcs", True)
            print(f"Exibição de NPCs: {'Ativada' if config['show_npcs'] else 'Desativada'}")
            # Limpar objetos para forçar recriação
            for obj in game.objects.copy():
                if isinstance(obj, PlayerBlip):
                    continue
                obj.delete()
                game.objects.remove(obj)
            
            # Forçar uma atualização completa do cache de atores para recarregar os NPCs
            if config["show_npcs"]:
                game.actor_cache = frozenset()  # Limpar o cache para forçar redescoberta


pyglet.clock.schedule_interval(refresh_radar, 1 / FPS)
pyglet.app.run(interval=1 / FPS)
