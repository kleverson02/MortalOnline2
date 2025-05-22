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

# Constante para controlar a rotação do radar
ENABLE_ROTATION = True  # Defina como False para desativar a rotação

# Cores
COLOR_PLAYER = (255, 0, 0)       # Vermelho
COLOR_GHOST = (0, 255, 0)        # Verde para jogadores fantasmas
COLOR_LOCAL = (0, 0, 255)        # Azul
COLOR_BACKGROUND = (30, 30, 30)  # Cinza escuro
COLOR_GRID = (60, 60, 60)        # Cinza

class SimpleRadar(pyglet.window.Window):
    def __init__(self):
        super().__init__(WINDOW_SIZE, WINDOW_SIZE, caption="Radar Simples")
        self.batch = pyglet.graphics.Batch()
        self.mem = Reader("GameThread")
        
        # Fator de zoom (1.0 = normal, < 1.0 = zoom in, > 1.0 = zoom out)
        self.zoom_factor = 1.0
        self.current_range = RANGE
        
        # Rotação manual do radar (em graus)
        self.manual_rotation = 0.0
        
        # Criar círculos de alcance
        self.rings = []
        self.ring_ranges = [5000, 10000, 15000]
        for r in self.ring_ranges:
            ring = shapes.Circle(
                CENTER[0], CENTER[1], 
                (WINDOW_SIZE / 2) * (r / RANGE),
                color=COLOR_GRID, batch=self.batch
            )
            ring.opacity = 128
            self.rings.append(ring)
        
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
            
            # Ler o array de atores
            actor_array, actor_count = self.mem.read(persistent_level + offsets.ActorArray, "QI")
            
            # Encontrar o jogador "Pombagira" para usar como jogador local
            local_pos = (0, 0, 0)
            local_rot = 0  # Rotação do jogador local (em radianos)
            local_actor = None
            local_root = None
            
            # Obter o PlayerController e a câmera
            game_instance = self.mem.read(uworld + offsets.OwningGameInstance, "Q")
            local_players = self.mem.read(game_instance + offsets.LocalPlayers, "Q")
            local_player = self.mem.read(local_players, "Q")
            controller = self.mem.read(local_player + offsets.PlayerController, "Q")
            camera_manager = self.mem.read(controller + offsets.PlayerCameraManager, "Q")
            
            # Tentar obter a rotação da câmera
            try:
                if camera_manager and camera_manager > 0x10000000:
                    # Tentar diferentes offsets para a rotação da câmera
                    camera_cache = self.mem.read(camera_manager + offsets.CameraCachePrivate, "Q")
                    
                    # Tentar ler diretamente do CameraCachePrivate
                    if camera_cache and camera_cache > 0x10000000:
                        try:
                            # Tentar ler a rotação como 3 floats em diferentes offsets
                            for rot_offset in [0x10, 0x20, 0x30, 0x40]:
                                try:
                                    camera_rot = self.mem.read(camera_cache + rot_offset, "3f")
                                    if camera_rot and all(-360 < r < 360 for r in camera_rot):
                                        # O segundo valor (índice 1) geralmente é o yaw
                                        local_rot = math.radians(camera_rot[1])
                                        print(f"Rotação da câmera encontrada em cache+0x{rot_offset:X}: {math.degrees(local_rot):.1f}°")
                                        break
                                except:
                                    pass
                        except:
                            pass
                    
                    # Se não encontrou no cache, tentar diretamente no CameraManager
                    if local_rot == 0:
                        for rot_offset in [offsets.CameraRotation, offsets.CameraViewRotation, 
                                          offsets.CameraRotation2, offsets.CameraRotation3]:
                            try:
                                # Tentar ler como 3 floats (pitch, yaw, roll)
                                camera_rot = self.mem.read(camera_manager + rot_offset, "3f")
                                if camera_rot and all(-360 < r < 360 for r in camera_rot):
                                    # O segundo valor (índice 1) é o yaw (rotação no eixo Z)
                                    local_rot = math.radians(camera_rot[1])
                                    print(f"Rotação da câmera encontrada: {math.degrees(local_rot):.1f}° (offset: 0x{rot_offset:X})")
                                    break
                            except:
                                pass
            except Exception as e:
                print(f"Erro ao acessar camera_manager: {e}")
            
            # Procurar por Pombagira entre os atores
            for i in range(min(actor_count, 1000)):
                actor = self.mem.read(actor_array + (i * 8), "Q")
                if not actor or actor < 0x10000000:
                    continue
                    
                try:
                    # Verificar se é um jogador
                    key = self.mem.read(actor + 0x18, "2H")
                    block = key[1] * 8
                    offset = key[0] * 2
                    block_ptr = self.mem.read(offsets.GNames + block, "Q")
                    name_len = self.mem.read(block_ptr + offset, "H") >> 6
                    fname = self.mem.read_string(block_ptr + offset + 2, name_len)
                    
                    if "BP_PlayerCharacter_C" in fname:
                        # Tentar ler o nome do jogador
                        try:
                            name_addr, name_length = self.mem.read(actor + offsets.CreatureName, "QB")
                            if name_addr > 0x10000000 and 0 < name_length < 50:
                                name_bytes = max(0, name_length * 2 - 2)
                                name = self.mem.read_string(name_addr, name_bytes, encoding="utf-16")
                                
                                # Se encontrarmos Pombagira, usar como jogador local
                                if name == "Pombagira":
                                    local_actor = actor
                                    local_root = self.mem.read(actor + offsets.RootComponent, "Q")
                                    if local_root and local_root > 0x10000000:
                                        try:
                                            pos = self.mem.read(local_root + offsets.RootPos, "3d")
                                            if all(-1000000 < p < 1000000 for p in pos):
                                                local_pos = pos
                                                break
                                        except:
                                            pass
                        except:
                            pass
                except:
                    continue
            
            # Atualizar informações
            self.info_label.text = f"Atores: {actor_count} | Local: {local_pos[0]:.1f}, {local_pos[1]:.1f} | Rotação: {self.manual_rotation}° | Alcance: {self.current_range:.0f} | Zoom: {1/self.zoom_factor:.1f}x"
            
            # Encontrar outros jogadores
            players_found = 0
            
            for i in range(min(actor_count, 1000)):
                actor = self.mem.read(actor_array + (i * 8), "Q")
                if not actor or actor == local_actor or actor < 0x10000000:
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
                    if "BP_PlayerCharacter" in fname:
                        # Tentar ler o RootComponent
                        root_component = self.mem.read(actor + offsets.RootComponent, "Q")
                        if not root_component or root_component < 0x10000000:
                            continue
                            
                        # Ler a posição
                        pos = self.mem.read(root_component + offsets.RootPos, "3d")
                        
                        # Verificar se a posição parece válida
                        if not all(-1000000 < p < 1000000 for p in pos):
                            continue
                        
                        # Verificar se o jogador é um fantasma
                        is_ghost = False
                        try:
                            ghost_value = self.mem.read(actor + offsets.IsGhost, "?")
                            is_ghost = bool(ghost_value)
                        except:
                            pass
                        
                        # Tentar ler o nome do jogador
                        name = "Jogador"
                        try:
                            name_addr, name_length = self.mem.read(actor + offsets.CreatureName, "QB")
                            if name_addr > 0x10000000 and 0 < name_length < 50:
                                name_bytes = max(0, name_length * 2 - 2)
                                name = self.mem.read_string(name_addr, name_bytes, encoding="utf-16")
                        except:
                            pass
                        
                        # Calcular posição relativa ao jogador local
                        dx = pos[0] - local_pos[0]
                        dy = pos[1] - local_pos[1]
                        
                        # Calcular distância
                        dist = math.sqrt(dx*dx + dy*dy)
                        
                        # Ignorar jogadores muito distantes (considerando o zoom)
                        if dist > self.current_range:
                            continue
                        
                        # Calcular ângulo relativo
                        angle = math.atan2(dy, dx)
                        
                        # Aplicar a rotação manual (convertendo de graus para radianos)
                        angle -= math.radians(self.manual_rotation)
                        
                        # Adicionar um debug para verificar os valores
                        # if players_found == 0:  # Apenas para o primeiro jogador encontrado
                        #     print(f"Debug - dx: {dx}, dy: {dy}, angle: {math.degrees(angle)}, rotação manual: {self.manual_rotation}°")
                        
                        # Calcular posição na tela com zoom e rotação
                        screen_dist = (dist / self.current_range) * (WINDOW_SIZE / 2)
                        x = CENTER[0] + math.cos(angle) * screen_dist
                        y = CENTER[1] + math.sin(angle) * screen_dist
                        
                        # Criar marcador com cor baseada no estado de fantasma
                        marker_color = COLOR_GHOST if is_ghost else COLOR_PLAYER
                        marker = shapes.Circle(x, y, 4, color=marker_color, batch=self.batch)
                        self.player_markers.append(marker)
                        
                        # Criar rótulo com indicador de fantasma
                        ghost_indicator = " [G]" if is_ghost else ""
                        label = pyglet.text.Label(
                            name + ghost_indicator,
                            font_name='Arial',
                            font_size=8,
                            x=x, y=y + 10,
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
    
    def on_key_press(self, symbol, modifiers):
        """Trata eventos de teclas pressionadas"""
        if symbol == pyglet.window.key.PAGEUP:
            # Zoom in (reduz o alcance)
            self.zoom_factor *= 0.8
            self.current_range = RANGE * self.zoom_factor
            self.update_rings()
            self.info_label.text += f" | Zoom: {1/self.zoom_factor:.1f}x"
        elif symbol == pyglet.window.key.PAGEDOWN:
            # Zoom out (aumenta o alcance)
            self.zoom_factor *= 1.25
            self.current_range = RANGE * self.zoom_factor
            self.update_rings()
            self.info_label.text += f" | Zoom: {1/self.zoom_factor:.1f}x"
        elif symbol == pyglet.window.key.LEFT:
            # Girar o radar para a esquerda
            self.manual_rotation += 15
            if self.manual_rotation >= 360:
                self.manual_rotation -= 360
            self.info_label.text += f" | Rotação: {self.manual_rotation}°"
        elif symbol == pyglet.window.key.RIGHT:
            # Girar o radar para a direita
            self.manual_rotation -= 15
            if self.manual_rotation < 0:
                self.manual_rotation += 360
            self.info_label.text += f" | Rotação: {self.manual_rotation}°"
        elif symbol == pyglet.window.key.R:
            # Resetar a rotação manual
            self.manual_rotation = 0
            self.info_label.text += f" | Rotação resetada"
    
    def update_rings(self):
        """Atualiza os círculos de alcance com base no zoom atual"""
        for i, r in enumerate(self.ring_ranges):
            radius = (WINDOW_SIZE / 2) * (r / self.current_range)
            self.rings[i].radius = radius
    
    def on_draw(self):
        """Desenha a janela"""
        self.clear()
        self.batch.draw()

if __name__ == "__main__":
    window = SimpleRadar()
    pyglet.app.run()