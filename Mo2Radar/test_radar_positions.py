#!/usr/bin/env python3
import math
import time
import pyglet
from pyglet import shapes
from lib.memory import Reader
from lib import offsets

# Configurações da janela
WINDOW_SIZE = 800
CENTER = (WINDOW_SIZE // 2, WINDOW_SIZE // 2)
RANGE = 20000  # Alcance máximo do radar em unidades do jogo

# Cores
COLOR_PLAYER = (255, 0, 0)       # Vermelho
COLOR_LOCAL = (0, 0, 255)        # Azul
COLOR_BACKGROUND = (30, 30, 30)  # Cinza escuro
COLOR_GRID = (60, 60, 60)        # Cinza

def distance(pos1, pos2):
    """Calcula a distância entre duas posições 3D"""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(pos1, pos2)))

def world_to_screen(pos, local_pos, yaw):
    """Converte coordenadas do mundo para coordenadas da tela"""
    # Calcular posição relativa ao jogador local
    rel_x = pos[0] - local_pos[0]
    rel_y = pos[1] - local_pos[1]
    
    # Rotacionar com base no yaw do jogador
    rad_yaw = math.radians(yaw)
    sin_yaw = math.sin(rad_yaw)
    cos_yaw = math.cos(rad_yaw)
    
    rot_x = rel_x * cos_yaw - rel_y * sin_yaw
    rot_y = rel_x * sin_yaw + rel_y * cos_yaw
    
    # Escalar para o tamanho da janela e centralizar
    scale = (WINDOW_SIZE / 2) / RANGE
    screen_x = CENTER[0] + rot_x * scale
    screen_y = CENTER[1] + rot_y * scale
    
    return screen_x, screen_y

class RadarWindow(pyglet.window.Window):
    def __init__(self):
        super().__init__(WINDOW_SIZE, WINDOW_SIZE, caption="Teste de Radar")
        self.batch = pyglet.graphics.Batch()
        self.mem = Reader("GameThread")
        
        # Criar círculos de alcance
        self.rings = []
        ranges = [5000, 10000, 15000]
        for r in ranges:
            ring = shapes.Circle(
                CENTER[0], CENTER[1], 
                (WINDOW_SIZE / 2) * (r / RANGE),
                color=COLOR_GRID, batch=self.batch
            )
            ring.opacity = 128
            self.rings.append(ring)
        
        # Linhas de direção
        self.directions = []
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x = math.cos(rad) * WINDOW_SIZE / 2
            y = math.sin(rad) * WINDOW_SIZE / 2
            line = shapes.Line(
                CENTER[0], CENTER[1],
                CENTER[0] + x, CENTER[1] + y,
                color=COLOR_GRID, batch=self.batch
            )
            line.opacity = 128
            self.directions.append(line)
            
            # Adicionar rótulos de direção
            labels = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            label = pyglet.text.Label(
                labels[angle // 45],
                font_name='Arial',
                font_size=10,
                x=CENTER[0] + x * 1.1,
                y=CENTER[1] + y * 1.1,
                anchor_x='center', anchor_y='center',
                color=(200, 200, 200, 255),
                batch=self.batch
            )
            self.directions.append(label)
        
        # Marcador do jogador local
        self.local_marker = shapes.Circle(
            CENTER[0], CENTER[1], 6, color=COLOR_LOCAL, batch=self.batch
        )
        
        # Rótulo de informações
        self.info_label = pyglet.text.Label(
            'Carregando...',
            font_name='Arial',
            font_size=12,
            x=10, y=WINDOW_SIZE - 20,
            width=WINDOW_SIZE - 20,
            multiline=True,
            batch=self.batch
        )
        
        # Lista de marcadores de jogadores
        self.player_markers = []
        
        # Programar atualização
        pyglet.clock.schedule_interval(self.update_players, 0.5)
    
    def update_players(self, dt):
        """Atualiza as posições dos jogadores"""
        try:
            # Limpar marcadores antigos
            for marker in self.player_markers:
                marker.delete()
            self.player_markers.clear()
            
            # Obter o UWorld
            uworld = self.mem.read(offsets.GWorld, "Q")
            persistent_level = self.mem.read(uworld + offsets.PersistentLevel, "Q")
            
            # Obter o jogador local
            game_instance = self.mem.read(uworld + offsets.OwningGameInstance, "Q")
            local_players = self.mem.read(game_instance + offsets.LocalPlayers, "Q")
            local_player = self.mem.read(local_players, "Q")
            controller = self.mem.read(local_player + offsets.PlayerController, "Q")
            local_pawn = self.mem.read(controller + offsets.AcknowledgedPawn, "Q")
            
            # Obter a posição e rotação do jogador local
            local_root = self.mem.read(local_pawn + offsets.RootComponent, "Q")
            local_pos = self.mem.read(local_root + offsets.RootPos, "3d")
            
            # Obter a câmera para o yaw
            camera = self.mem.read(controller + offsets.PlayerCameraManager, "Q")
            _, _, _, _, yaw, _ = self.mem.read(camera + offsets.CameraCachePrivate, "6f")
            
            # Ler o array de atores
            actor_array, actor_count = self.mem.read(persistent_level + offsets.ActorArray, "QI")
            
            # Atualizar informações
            self.info_label.text = f"Posição local: {local_pos[0]:.1f}, {local_pos[1]:.1f}, {local_pos[2]:.1f} | Yaw: {yaw:.1f}°"
            
            # Encontrar jogadores
            players_found = 0
            
            for i in range(min(actor_count, 1000)):
                actor = self.mem.read(actor_array + (i * 8), "Q")
                if not actor or actor == local_pawn or actor < 0x10000000:
                    continue
                    
                try:
                    # Ler o FName key
                    key = self.mem.read(actor + 0x18, "2H")
                    
                    # Recuperar o nome do FName
                    block = key[1] * 8
                    offset = key[0] * 2
                    
                    block_ptr = self.mem.read(offsets.GNames + block, "Q")
                    name_len = self.mem.read(block_ptr + offset, "H") >> 6
                    fname = self.mem.read_string(block_ptr + offset + 2, name_len)
                    
                    # Verificar se é um jogador
                    if "BP_PlayerCharacter" in fname or "Character" in fname:
                        # Tentar ler o RootComponent
                        root_component = self.mem.read(actor + offsets.RootComponent, "Q")
                        if not root_component or root_component < 0x10000000:
                            continue
                            
                        # Ler a posição
                        pos = self.mem.read(root_component + offsets.RootPos, "3d")
                        
                        # Verificar se a posição parece válida
                        if not all(-1000000 < p < 1000000 for p in pos):
                            continue
                            
                        # Calcular distância até o jogador local
                        dist = distance(local_pos, pos)
                        if dist > RANGE:
                            continue
                        
                        # Tentar ler o nome
                        name = "Jogador"
                        try:
                            name_addr, name_length = self.mem.read(actor + offsets.CreatureName, "QB")
                            if name_addr > 0x10000000 and 0 < name_length < 50:
                                name_bytes = max(0, name_length * 2 - 2)
                                name = self.mem.read_string(name_addr, name_bytes, encoding="utf-16")
                        except:
                            pass
                        
                        # Converter para coordenadas da tela
                        screen_x, screen_y = world_to_screen(pos, local_pos, yaw)
                        
                        # Verificar se está dentro da janela
                        if 0 <= screen_x <= WINDOW_SIZE and 0 <= screen_y <= WINDOW_SIZE:
                            # Criar marcador
                            marker = shapes.Circle(screen_x, screen_y, 4, color=COLOR_PLAYER, batch=self.batch)
                            self.player_markers.append(marker)
                            
                            # Criar rótulo
                            label = pyglet.text.Label(
                                f"{name}\n{dist:.1f}m",
                                font_name='Arial',
                                font_size=8,
                                x=screen_x, y=screen_y + 10,
                                anchor_x='center', anchor_y='bottom',
                                color=(255, 255, 255, 255),
                                batch=self.batch
                            )
                            self.player_markers.append(label)
                            
                            players_found += 1
                except:
                    continue
            
            # Atualizar contador
            self.info_label.text += f" | Jogadores: {players_found}"
            
        except Exception as e:
            self.info_label.text = f"Erro: {str(e)}"
    
    def on_draw(self):
        """Desenha a janela"""
        self.clear()
        self.batch.draw()

if __name__ == "__main__":
    window = RadarWindow()
    pyglet.app.run()