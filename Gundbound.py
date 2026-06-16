# ==============================================================================
# ESTUDIO DE ARQUITECTURA DE SOFTWARE - SIMULADOR GUNBOUND V6 (EDICIÓN ESTABLE)
# REQUISITO: CONTROL DE CALIDAD, TESTING E IMPLANTACIÓN DE SISTEMAS
# ==============================================================================

import pygame
import math
import random
import sys
import array
import os

# ==============================================================================
# CONFIGURACIÓN Y CONSTANTES GLOBALISTAS DEL ENTORNO
# ==============================================================================
WIDTH = 1024
HEIGHT = 768
FPS = 60

# Paleta Cromática Institucional de Respaldo (RGB)
COLOR_WHITE       = (255, 255, 255)
COLOR_BLACK       = (0, 0, 0)
COLOR_SKY_TOP     = (10, 17, 31)
COLOR_SKY_MID     = (24, 42, 71)
COLOR_SKY_BOTTOM  = (52, 82, 122)
COLOR_TERRAIN     = (46, 117, 89)
COLOR_TERRAIN_SUB = (84, 62, 44)
COLOR_BULLET      = (254, 211, 48)
COLOR_EXPLOSION   = (235, 94, 40)
COLOR_TEXT_UI     = (245, 246, 250)
COLOR_GOLD        = (255, 215, 0)

# ==============================================================================
# GESTOR CENTRAL DE ASSETS CON REDUNDANCIA PASIVA (FALLBACK SYSTEM)
# ==============================================================================
class AssetManager:
    """
    Carga de forma segura y centralizada los sprites del sistema.
    Aplica programación defensiva para evitar excepciones por ausencia de archivos.
    """
    def __init__(self):
        self.use_sprites = True
        self.sprites = {}
        self.load_all_assets()

    def safe_load(self, path, scale_dims=None):
        """Carga una imagen aislada aplicando validación perimetral de rutas."""
        if not os.path.exists(path):
            self.use_sprites = False
            return None
        try:
            img = pygame.image.load(path).convert_alpha()
            if scale_dims:
                img = pygame.transform.scale(img, scale_dims)
            return img
        except pygame.error:
            self.use_sprites = False
            return None

    def load_all_assets(self):
        mobiles = ['Knight', 'Mage', 'Dragon', 'Heavy']
        body_dims = (42, 24)
        cannon_dims = (26, 8)
        
        self.sprites['muzzle_flash'] = self.safe_load("assets/muzzle_flash.png", (20, 20))

        for mob in mobiles:
            m_lower = mob.lower()
            self.sprites[mob] = {
                'idle':   self.safe_load(f"assets/{m_lower}_idle.png", body_dims),
                'move1':  self.safe_load(f"assets/{m_lower}_move1.png", body_dims),
                'move2':  self.safe_load(f"assets/{m_lower}_move2.png", body_dims),
                'cannon': self.safe_load(f"assets/{m_lower}_cannon.png", cannon_dims)
            }
            if (not self.sprites[mob]['idle'] or not self.sprites[mob]['move1'] or 
                not self.sprites[mob]['move2'] or not self.sprites[mob]['cannon']):
                self.use_sprites = False


# ==============================================================================
# AUDIO SINTÉTICO PROCEDIMENTAL BINARIO
# ==============================================================================
class SoundGenerator:
    @staticmethod
    def init_mixer():
        try: pygame.mixer.init(frequency=22050, size=-16, channels=1)
        except Exception: pass

    @staticmethod
    def create_shoot_sound():
        sample_rate = 22050
        duration = 0.12
        num_samples = int(duration * sample_rate)
        buf = array.array('h', [0] * num_samples)
        for i in range(num_samples):
            t = i / sample_rate
            freq = 480.0 - (t / duration) * 300.0
            val = math.sin(2 * math.pi * freq * t)
            buf[i] = int(val * 11000 * (1.0 - t/duration))
        try: return pygame.mixer.Sound(buffer=buf)
        except Exception: return None

    @staticmethod
    def create_explosion_sound():
        sample_rate = 22050
        duration = 0.35
        num_samples = int(duration * sample_rate)
        buf = array.array('h', [0] * num_samples)
        for i in range(num_samples):
            t = i / sample_rate
            noise = random.uniform(-1.0, 1.0)
            val = noise * (1.0 - t / duration) ** 2.5
            buf[i] = int(val * 13000)
        try: return pygame.mixer.Sound(buffer=buf)
        except Exception: return None


# ==============================================================================
# SISTEMA DE PARTÍCULAS RADIALES
# ==============================================================================
class Particle:
    def __init__(self, x, y, color, vx=None, vy=None):
        self.x = float(x)
        self.y = float(y)
        if vx is None or vy is None:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.0, 6.5)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
        else:
            self.vx = vx
            self.vy = vy
        self.color = color
        self.radius = random.uniform(3, 6)
        self.alpha = 255
        self.decay = random.uniform(4, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05
        self.alpha -= self.decay

    def draw(self, surface):
        if self.alpha > 0 and self.radius > 0:
            ratio = max(0.0, min(1.0, self.alpha / 255.0))
            c = (min(255, max(0, int(self.color[0] * ratio))),
                 min(255, max(0, int(self.color[1] * ratio))),
                 min(255, max(0, int(self.color[2] * ratio))))
            pygame.draw.circle(surface, c, (int(self.x), int(self.y)), int(self.radius))


# ==============================================================================
# ANIMACIÓN DE EXPLOSIÓN CROMÁTICA EXPANSIVA
# ==============================================================================
class ExplosionAnimation:
    def __init__(self, x, y, max_radius):
        self.x = float(x)
        self.y = float(y)
        self.max_radius = float(max_radius)
        self.current_radius = 0.0
        self.duration_frames = 40  
        self.current_frame = 0
        self.is_finished = False

    def update(self):
        self.current_frame += 1
        ratio = self.current_frame / self.duration_frames
        self.current_radius = self.max_radius * ratio
        if self.current_frame >= self.duration_frames:
            self.is_finished = True

    def draw(self, surface):
        ratio = self.current_frame / self.duration_frames
        if ratio >= 1.0: return

        if ratio < 0.25:
            factor = ratio / 0.25
            r = int(235 * (1.0 - factor) + 255 * factor)
            g = int(94 * (1.0 - factor) + 220 * factor)
            b = int(40 * (1.0 - factor) + 50 * factor)
        elif ratio < 0.65:
            factor = (ratio - 0.25) / 0.40
            r = 255
            g = int(220 * (1.0 - factor) + 30 * factor)
            b = int(50 * (1.0 - factor) + 10 * factor)
        else:
            factor = (ratio - 0.65) / 0.35
            r = int(230 * (1.0 - factor))
            g = int(30 * (1.0 - factor))
            b = int(10 * (1.0 - factor))

        color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
        if self.current_radius > 2:
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.current_radius))


# ==============================================================================
# CONFIGURACIÓN DE ARMAMENTO EXCLUSIVO POR PERFIL
# ==============================================================================
class WeaponProfile:
    def __init__(self, name, damage, radius, speed_mult, cost, desc, special_type="normal"):
        self.name = name
        self.damage = damage       
        self.radius = radius       
        self.speed_mult = speed_mult
        self.cost = cost
        self.desc = desc
        self.special_type = special_type  

CHARACTER_WEAPONS = {
    'Knight': [
        WeaponProfile("Shot Básico", damage=30, radius=26, speed_mult=1.0, cost=0, desc="Munición estándar."),
        WeaponProfile("Missile Táctico", damage=46, radius=38, speed_mult=1.05, cost=35, desc="Misil perforador azul."),
        WeaponProfile("Double Shot", damage=25, radius=24, speed_mult=1.0, cost=65, desc="Lanza 2 misiles de impacto continuo.", special_type="double"),
        WeaponProfile("Shield Strike", damage=50, radius=32, speed_mult=1.18, cost=75, desc="Impacto cinético lineal rápido."),
        WeaponProfile("Holy Bomb", damage=68, radius=58, speed_mult=0.9, cost=130, desc="Explosión bendita masiva.")
    ],
    'Mage': [
        WeaponProfile("Shot Básico", damage=30, radius=26, speed_mult=1.0, cost=0, desc="Munición estándar."),
        WeaponProfile("Fireball Plasma", damage=52, radius=52, speed_mult=0.95, cost=50, desc="Onda ígnea expansiva."),
        WeaponProfile("Thunder Strike", damage=55, radius=36, speed_mult=1.1, cost=80, desc="Rayo electromagnético vertical.", special_type="thunder"),
        WeaponProfile("Magic Arrow", damage=38, radius=20, speed_mult=1.45, cost=45, desc="Saeta de plasma veloz."),
        WeaponProfile("Meteor Inbound", damage=76, radius=65, speed_mult=0.85, cost=140, desc="Meteoro denso de alta destrucción.")
    ],
    'Dragon': [
        WeaponProfile("Shot Básico", damage=30, radius=26, speed_mult=1.0, cost=0, desc="Munición estándar."),
        WeaponProfile("Poison Shot", damage=44, radius=34, speed_mult=1.1, cost=40, desc="Plasma ácido corrosivo."),
        WeaponProfile("Flame Breath", damage=48, radius=46, speed_mult=1.0, cost=55, desc="Fuego místico molecular."),
        WeaponProfile("Dragon Fang", damage=56, radius=38, speed_mult=1.22, cost=85, desc="Perforador colmillar pesado."),
        WeaponProfile("Earthquake", damage=62, radius=68, speed_mult=0.88, cost=120, desc="Onda sismológica destructora.")
    ],
    'Heavy': [
        WeaponProfile("Shot Básico", damage=30, radius=26, speed_mult=1.0, cost=0, desc="Munición estándar."),
        WeaponProfile("Atomic Bomb", damage=92, radius=92, speed_mult=0.7, cost=200, desc="Ojiva de destrucción masiva."),
        WeaponProfile("Big Missile", damage=58, radius=48, speed_mult=0.92, cost=70, desc="Fragmentación pesada."),
        WeaponProfile("Machine Gun", damage=18, radius=20, speed_mult=1.28, cost=60, desc="Ráfaga continua de 3 disparos.", special_type="machinegun"),
        WeaponProfile("Bunker Buster", damage=48, radius=42, speed_mult=1.12, cost=90, desc="Taladra antes de estallar.", special_type="buster")
    ]
}


# ==============================================================================
# ENTIDAD OPERACIONAL: CLASE TANK REFACTORIZADA (INCLINACIÓN DINÁMICA DE CHASIS)
# ==============================================================================
class Tank:
    def __init__(self, x, mobile_type, name):
        self.x = float(x)
        self.y = 0.0
        self.mobile_type = mobile_type
        self.name = name
        self.width = 42
        self.height = 24
        
        self.max_health = 135 if mobile_type == 'Heavy' else 100
        self.health = self.max_health
        self.shield = 0
        self.gold = 300
        self.next_damage_mult = 1.0
        
        # Inclinaciones y Ángulos (Alineación Estricta al Gunbound Original)
        self.base_angle = 0.0  # Ángulo de inclinación del terreno actual
        self.angle = 45.0 if x < WIDTH/2 else 135.0  # Ángulo relativo controlado por el usuario
        
        self.power = 0.0
        self.speed = 1.5 if mobile_type == 'Heavy' else (2.4 if mobile_type == 'Knight' else 2.0)
        self.wheel_rotation = 0.0
        self.recoil_offset = 0.0
        
        self.vy = 0.0
        self.is_moving = False
        self.last_anim_tick = 0
        self.anim_toggle = False  
        self.muzzle_flash_frames = 0
        
        if mobile_type == 'Knight': self.color = (41, 128, 185)
        elif mobile_type == 'Mage': self.color = (192, 41, 43)
        elif mobile_type == 'Dragon': self.color = (39, 174, 96)
        else: self.color = (211, 84, 0)

    def calculate_terrain_slope(self, terrain):
        """Calcula trigonométricamente la inclinación analizando las huellas de las ruedas."""
        ix = max(0, min(int(self.x), WIDTH - 1))
        # Si la unidad está suspendida en el aire, tiende a estabilizar el chasis horizontalmente
        if self.y < float(terrain.heights[ix]):
            return 0.0
            
        # Puntos de muestreo simétricos bajo las orugas externas (Offset de 14px)
        x_left = max(0, min(int(self.x - 14), WIDTH - 1))
        x_right = max(0, min(int(self.x + 14), WIDTH - 1))
        
        y_left = terrain.heights[x_left]
        y_right = terrain.heights[x_right]
        
        dx = x_right - x_left
        dy = y_right - y_left  # Inversión cartesiana implícita de Pygame (Y crece hacia abajo)
        
        if dx == 0: return 0.0
        
        # Obtener el ángulo en grados e invertir dy para ajustar a rotación antihoraria estándar
        target_angle = math.degrees(math.atan2(-dy, dx))
        # Delimitador de seguridad operacional para evitar volteos inverosímiles
        return max(-35.0, min(target_angle, 35.0))

    def update_position(self, terrain):
        ix = max(0, min(int(self.x), WIDTH - 1))
        ground_y = float(terrain.heights[ix])
        
        # Algoritmo de vectorización por gravedad (Caída libre táctica)
        if self.y < ground_y:
            self.vy += 0.38  
            self.y += self.vy
            if self.y >= ground_y:
                self.y = ground_y
                self.vy = 0.0
        else:
            self.y = ground_y
            self.vy = 0.0
            
        # Suavizado cinemático de inclinación mediante interpolación lineal (LERP de 15% por frame)
        target_slope = self.calculate_terrain_slope(terrain)
        self.base_angle += (target_slope - self.base_angle) * 0.15

        if self.recoil_offset > 0: self.recoil_offset -= 0.6
        if self.muzzle_flash_frames > 0: self.muzzle_flash_frames -= 1

    def move(self, direction, terrain):
        self.x += direction * self.speed
        self.wheel_rotation += direction * 0.3
        self.is_moving = True
        
        now = pygame.time.get_ticks()
        if now - self.last_anim_tick > 120:
            self.anim_toggle = not self.anim_toggle
            self.last_anim_tick = now

        half_w = self.width / 2
        if self.x < half_w: self.x = half_w
        elif self.x > WIDTH - half_w: self.x = WIDTH - half_w
        self.update_position(terrain)

    def rotate_point_helper(self, cx, cy, px, py, angle_deg):
        """Función auxiliar para rotar vértices geométricos en el sistema de fallback."""
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        dx = px - cx
        dy = py - cy
        rx = cx + dx * cos_a - dy * sin_a
        ry = cy + dx * sin_a + dy * cos_a
        return (int(rx), int(ry))

    def draw(self, surface, is_active, asset_mgr):
        tx = int(self.x)
        ty = int(self.y)
        
        # Ajuste lineal por retroceso
        rad_recoil = math.radians(self.base_angle + self.angle)
        draw_x = tx - int(math.cos(rad_recoil) * self.recoil_offset)
        draw_y = ty + int(math.sin(rad_recoil) * self.recoil_offset)

        pivot_x = draw_x
        pivot_y = draw_y - 12

        # ÁNGULO ABSOLUTO MATEMÁTICO: Inclinación de Chasis + Ángulo Relativo de Entrada
        abs_angle = self.base_angle + self.angle
        abs_rad = math.radians(abs_angle)
        barrel_len = 24
        bx = pivot_x + math.cos(abs_rad) * barrel_len
        by = pivot_y - math.sin(abs_rad) * barrel_len

        # 1. RENDERIZADO DEL CAÑÓN ROTATIVO ABSOLUTO
        if asset_mgr.use_sprites:
            orig_cannon = asset_mgr.sprites[self.mobile_type]['cannon']
            # Rotar usando el ángulo absoluto sumado
            rotated_cannon = pygame.transform.rotate(orig_cannon, abs_angle)
            rot_rect = rotated_cannon.get_rect()
            rot_rect.center = (pivot_x + math.cos(abs_rad) * (barrel_len / 2), pivot_y - math.sin(abs_rad) * (barrel_len / 2))
            surface.blit(rotated_cannon, rot_rect.topleft)
        else:
            pygame.draw.line(surface, (236, 240, 241), (pivot_x, pivot_y), (int(bx), int(by)), 4)

        # 2. RENDERIZADO DEL CHASIS (ROTADO SUAVEMENTE SEGÚN BASE_ANGLE)
        if asset_mgr.use_sprites:
            if not self.is_moving:
                frame_sprite = asset_mgr.sprites[self.mobile_type]['idle']
            else:
                frame_sprite = asset_mgr.sprites[self.mobile_type]['move1'] if self.anim_toggle else asset_mgr.sprites[self.mobile_type]['move2']
            
            # Rotación integrada de la matriz de pixeles de la superficie
            rotated_body = pygame.transform.rotate(frame_sprite, self.base_angle)
            body_rect = rotated_body.get_rect(center=(draw_x, draw_y - 10))
            surface.blit(rotated_body, body_rect.topleft)
        else:
            # Fallback Geométrico Rotado mediante Matrices de Vértices Vectoriales
            cx, cy = draw_x, draw_y - 10
            # Dibujo simplificado de caja transformable de respaldo
            p1 = self.rotate_point_helper(cx, cy, draw_x - 18, draw_y - 16, self.base_angle)
            p2 = self.rotate_point_helper(cx, cy, draw_x + 18, draw_y - 16, self.base_angle)
            p3 = self.rotate_point_helper(cx, cy, draw_x + 18, draw_y - 6, self.base_angle)
            p4 = self.rotate_point_helper(cx, cy, draw_x - 18, draw_y - 6, self.base_angle)
            pygame.draw.polygon(surface, self.color, [p1, p2, p3, p4])

            # Ruedas base rotadas de respaldo
            for wx in [-14, -5, 5, 14]:
                w_cx, w_cy = self.rotate_point_helper(cx, cy, draw_x + wx, draw_y - 4, self.base_angle)
                pygame.draw.circle(surface, (44, 62, 80), (w_cx, w_cy), 5)

        # 3. RENDERIZADO DEL MUZZLE FLASH EN LA ORIENTACIÓN ABSOLUTA
        if self.muzzle_flash_frames > 0:
            if asset_mgr.use_sprites and asset_mgr.sprites['muzzle_flash']:
                mf_sprite = asset_mgr.sprites['muzzle_flash']
                rotated_mf = pygame.transform.rotate(mf_sprite, abs_angle)
                mf_rect = rotated_mf.get_rect(center=(int(bx), int(by)))
                surface.blit(rotated_mf, mf_rect.topleft)
            else:
                pygame.draw.circle(surface, (254, 202, 87), (int(bx), int(by)), 9)
                pygame.draw.circle(surface, COLOR_WHITE, (int(bx), int(by)), 5)

        # 4. ELEMENTOS ESTÁTICOS DE INTERFAZ INTEGRADA (HP / SHIELD)
        bar_w = 46
        bx_pos = draw_x - bar_w // 2
        by_pos = draw_y - 42
        pygame.draw.rect(surface, (50, 50, 50), (bx_pos, by_pos, bar_w, 5))
        hp_ratio = max(0.0, min(1.0, self.health / self.max_health))
        pygame.draw.rect(surface, (46, 204, 113), (bx_pos, by_pos, int(bar_w * hp_ratio), 5))
        
        if self.shield > 0:
            sh_ratio = max(0.0, min(1.0, self.shield / 50.0))
            pygame.draw.rect(surface, (52, 152, 219), (bx_pos, by_pos + 6, int(bar_w * sh_ratio), 3))

        font_tag = pygame.font.SysFont("Arial", 11, bold=True)
        txt_name = font_tag.render(self.name, True, COLOR_WHITE)
        surface.blit(txt_name, (draw_x - txt_name.get_width() // 2, by_pos - 15))


# ==============================================================================
# FÍSICA BALÍSTICA DE ELEMENTOS DE PROYECCIÓN
# ==============================================================================
class Projectile:
    def __init__(self, x, y, angle, power, wind_x, weapon_profile, owner):
        self.x = float(x)
        self.y = float(y)
        self.profile = weapon_profile
        self.owner = owner
        
        rad = math.radians(angle)
        velocity_scalar = power * 0.25 * weapon_profile.speed_mult
        self.vx = velocity_scalar * math.cos(rad)
        self.vy = -velocity_scalar * math.sin(rad)
        
        self.gravity = 0.22
        self.wind_factor = 0.045
        self.wind_x = wind_x

    def update(self):
        self.vx += self.wind_x * self.wind_factor
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        color = (235, 94, 40) if self.profile.special_type == "thunder" else COLOR_BULLET
        radius = 6 if self.profile.radius > 60 else 3
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)


# ==============================================================================
# ESCENARIO TOPOGRÁFICO DESTRUCTIBLE (SISTEMA DE 5 MAPAS ALEATORIOS)
# ==============================================================================
class Terrain:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.heights = []
        self.map_type = random.randint(1, 5)  # Selección aleatoria obligatoria entre los 5 estilos
        self.generate_procedural_terrain()

    def generate_procedural_terrain(self):
        self.heights.clear()
        
        if self.map_type == 1:
            # 1. Terreno plano con colinas suaves
            base_level = self.height * 0.75
            for x in range(self.width):
                h = base_level + math.sin(x * 0.004) * 35 + math.sin(x * 0.012) * 10
                self.heights.append(int(max(self.height * 0.35, min(h, self.height * 0.92))))
                
        elif self.map_type == 2:
            # 2. Terreno montañoso con picos altos
            base_level = self.height * 0.60
            for x in range(self.width):
                h = base_level + math.sin(x * 0.006) * 165 + math.cos(x * 0.022) * 45
                self.heights.append(int(max(self.height * 0.25, min(h, self.height * 0.92))))
                
        elif self.map_type == 3:
            # 3. Terreno con valles profundos
            base_level = self.height * 0.52
            for x in range(self.width):
                h = base_level + math.sin(x * 0.003) * 150 + math.sin(x * 0.0015) * 95
                self.heights.append(int(max(self.height * 0.28, min(h, self.height * 0.92))))
                
        elif self.map_type == 4:
            # 4. Terreno ondulado tipo olas
            base_level = self.height * 0.70
            for x in range(self.width):
                h = base_level + math.sin(x * 0.032) * 55 + math.sin(x * 0.016) * 20
                self.heights.append(int(max(self.height * 0.35, min(h, self.height * 0.92))))
                
        else:
            # 5. Terreno con mesetas y plataformas (Quantized Step-Function)
            base_level = self.height * 0.65
            for x in range(self.width):
                steps = int(math.sin(x * 0.0055) * 4) * 38
                smooth_blend = math.sin(x * 0.02) * 8
                h = base_level + steps + smooth_blend
                self.heights.append(int(max(self.height * 0.32, min(h, self.height * 0.92))))

    def destroy(self, center_x, center_y, radius, vertical_shift=0):
        """Remoción circular matemática absoluta. Resuelve el bug de líneas residuales delgadas."""
        cx, cy = int(center_x), int(center_y) + int(vertical_shift)
        r = int(radius)
        start_x = max(0, cx - r)
        end_x = min(self.width, cx + r + 1)
        gold_gained = 0

        for x in range(start_x, end_x):
            dx = x - cx
            chord = math.sqrt(r**2 - dx**2)
            circle_bottom = cy + chord

            if self.heights[x] < circle_bottom:
                diff = int(circle_bottom - self.heights[x])
                gold_gained += min(diff, 8)
                # Remoción sólida de píxeles: Sincroniza el mapa de alturas a la base esférica exacta
                self.heights[x] = int(max(self.heights[x], circle_bottom))
                if self.heights[x] > self.height:
                    self.heights[x] = self.height
        return int(gold_gained * 0.22)

    def draw(self, surface):
        points = [(0, self.height)]
        for x in range(self.width):
            points.append((x, self.heights[x]))
        points.append((self.width - 1, self.height))

        pygame.draw.polygon(surface, COLOR_TERRAIN_SUB, points)
        for x in range(0, self.width, 2):
            pygame.draw.line(surface, COLOR_TERRAIN, (x, self.heights[x]), (x, self.heights[x] + 8), 2)


# ==============================================================================
# ORQUESTADOR CENTRAL DE FLUJO Y MÁQUINA DE ESTADOS (GAME MOTOR)
# ==============================================================================
class Game:
    STATE_MENU = 0
    STATE_CHARACTER_SELECT = 1
    STATE_PLAYING = 2
    STATE_GAME_OVER = 3

    SUBSTATE_AIMING = 0
    SUBSTATE_CHARGING = 1
    SUBSTATE_SHOP = 2
    SUBSTATE_FIRING = 3
    SUBSTATE_EXPLODING = 4

    def __init__(self):
        pygame.init()
        SoundGenerator.init_mixer()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Gunbound Core Ultimate V6 - Terrains & Slope Adaptive Edition")
        self.clock = pygame.time.Clock()
        
        self.asset_mgr = AssetManager()
        
        self.font_sm = pygame.font.SysFont("monospace", 14)
        self.font_main = pygame.font.SysFont("Arial", 20, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)

        self.snd_shoot = SoundGenerator.create_shoot_sound()
        self.snd_explosion = SoundGenerator.create_explosion_sound()

        self.state = Game.STATE_MENU
        
        self.mobiles_pool = ['Knight', 'Mage', 'Dragon', 'Heavy']
        self.p1_sel_idx = 0
        self.p2_sel_idx = 1
        self.selection_phase = 1 
        
        self.particles = []
        self.projectiles_queue = []
        self.current_explosion = None
        self.current_weapon_idx = {0: 0, 1: 0} 

        self.reset_game()

    def reset_game(self):
        self.terrain = Terrain(WIDTH, HEIGHT)
        self.particles.clear()
        self.projectiles_queue.clear()
        self.current_explosion = None
        
        p1_type = self.mobiles_pool[self.p1_sel_idx] if hasattr(self, 'p1_sel_idx') else 'Knight'
        p2_type = self.mobiles_pool[self.p2_sel_idx] if hasattr(self, 'p2_sel_idx') else 'Mage'

        self.player1 = Tank(WIDTH * 0.18, p1_type, "Player 1")
        self.player2 = Tank(WIDTH * 0.82, p2_type, "Player 2")
        
        self.player1.update_position(self.terrain)
        self.player2.update_position(self.terrain)
        
        self.tanks = [self.player1, self.player2]
        self.current_turn = 0
        self.substate = Game.SUBSTATE_AIMING
        self.turn_timer = 30.0
        self.randomize_wind()

    def randomize_wind(self):
        self.wind_x = random.uniform(-6.0, 6.0)

    def get_current_player(self):
        return self.tanks[self.current_turn]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if self.state == Game.STATE_MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = Game.STATE_CHARACTER_SELECT
                        self.selection_phase = 1
                
                elif self.state == Game.STATE_CHARACTER_SELECT:
                    if self.selection_phase == 1:
                        if event.key == pygame.K_LEFT: self.p1_sel_idx = (self.p1_sel_idx - 1) % 4
                        elif event.key == pygame.K_RIGHT: self.p1_sel_idx = (self.p1_sel_idx + 1) % 4
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            self.selection_phase = 2
                    elif self.selection_phase == 2:
                        if event.key == pygame.K_LEFT: self.p2_sel_idx = (self.p2_sel_idx - 1) % 4
                        elif event.key == pygame.K_RIGHT: self.p2_sel_idx = (self.p2_sel_idx + 1) % 4
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            self.reset_game()
                            self.state = Game.STATE_PLAYING

                elif self.state == Game.STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        self.state = Game.STATE_CHARACTER_SELECT
                        self.selection_phase = 1
                    elif event.key == pygame.K_ESCAPE:
                        self.state = Game.STATE_MENU

                elif self.state == Game.STATE_PLAYING:
                    if self.substate == Game.SUBSTATE_AIMING:
                        if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                            idx = int(event.unicode) - 1
                            if 0 <= idx < 5:
                                self.current_weapon_idx[self.current_turn] = idx
                        
                        elif event.key == pygame.K_t:
                            self.substate = Game.SUBSTATE_SHOP
                            
                        elif event.key == pygame.K_SPACE:
                            self.substate = Game.SUBSTATE_CHARGING
                            self.get_current_player().power = 0.0
                            
                        elif event.key == pygame.K_w: 
                            self.randomize_wind()
                            
                    elif self.substate == Game.SUBSTATE_SHOP:
                        player = self.get_current_player()
                        if event.key == pygame.K_t or event.key == pygame.K_ESCAPE:
                            self.substate = Game.SUBSTATE_AIMING
                        elif event.key == pygame.K_1 and player.gold >= 100:
                            player.gold -= 100
                            player.shield = min(50, player.shield + 25)
                        elif event.key == pygame.K_2 and player.gold >= 120:
                            player.gold -= 120
                            player.health = min(player.max_health, player.health + 30)
                        elif event.key == pygame.K_3 and player.gold >= 150:
                            player.gold -= 150
                            player.next_damage_mult = 1.5

            elif event.type == pygame.KEYUP:
                if self.state == Game.STATE_PLAYING and self.substate == Game.SUBSTATE_CHARGING:
                    if event.key == pygame.K_SPACE:
                        self.fire_weapon_sequence()

    def fire_weapon_sequence(self):
        player = self.get_current_player()
        weapons_list = CHARACTER_WEAPONS[player.mobile_type]
        w_profile = weapons_list[self.current_weapon_idx[self.current_turn]]
        
        if player.gold < w_profile.cost:
            self.substate = Game.SUBSTATE_AIMING
            return

        player.gold -= w_profile.cost
        
        # Disparo calculado usando el ángulo absoluto real (Base + Relativo)
        abs_angle = player.base_angle + player.angle
        rad = math.radians(abs_angle)
        sx = player.x + math.cos(rad) * 24
        sy = player.y - 12 - math.sin(rad) * 24
        
        player.recoil_offset = 9.0
        player.muzzle_flash_frames = 6 

        if self.snd_shoot:
            self.snd_shoot.play()

        if w_profile.special_type == "double":
            self.projectiles_queue.append(Projectile(sx, sy, abs_angle, player.power, self.wind_x, w_profile, player))
            self.projectiles_queue.append(Projectile(sx - math.cos(rad)*6, sy + math.sin(rad)*6, abs_angle, player.power * 0.92, self.wind_x, w_profile, player))
        elif w_profile.special_type == "machinegun":
            for idx in range(3):
                offset_scalar = idx * 5
                self.projectiles_queue.append(Projectile(sx - math.cos(rad)*offset_scalar, sy + math.sin(rad)*offset_scalar, abs_angle, player.power * (1.0 - idx*0.05), self.wind_x, w_profile, player))
        else:
            self.projectiles_queue.append(Projectile(sx, sy, abs_angle, player.power, self.wind_x, w_profile, player))

        self.substate = Game.SUBSTATE_FIRING

    def update_physics_and_logic(self):
        for p in self.particles[:]:
            p.update()
            if p.alpha <= 0: self.particles.remove(p)

        if self.state != Game.STATE_PLAYING: return

        for t in self.tanks:
            t.is_moving = False

        if self.substate == Game.SUBSTATE_AIMING:
            self.turn_timer -= 1.0 / FPS
            if self.turn_timer <= 0: self.end_turn_cycle()
            
            keys = pygame.key.get_pressed()
            p = self.get_current_player()
            if keys[pygame.K_LEFT]:  p.move(-1, self.terrain)
            if keys[pygame.K_RIGHT]: p.move(1, self.terrain)
            if keys[pygame.K_UP]:    p.angle = min(180.0, p.angle + 1.2)
            if keys[pygame.K_DOWN]:  p.angle = max(0.0, p.angle - 1.2)

        elif self.substate == Game.SUBSTATE_CHARGING:
            p = self.get_current_player()
            p.power += 1.8
            if p.power >= 100.0:
                p.power = 100.0
                self.fire_weapon_sequence()

        elif self.substate == Game.SUBSTATE_FIRING:
            if not self.projectiles_queue:
                self.substate = Game.SUBSTATE_AIMING
                return
            
            proj = self.projectiles_queue[0]
            
            # --- CCD / SUBSTEPPING CONTRA TUNELIZACIÓN EN COLISIONES DE TERRENO ---
            sub_steps = 5
            for _ in range(sub_steps):
                proj.vx += (proj.wind_x * proj.wind_factor) / sub_steps
                proj.vy += proj.gravity / sub_steps
                proj.x += proj.vx / sub_steps
                proj.y += proj.vy / sub_steps

                if proj.x < 0 or proj.x >= WIDTH or proj.y > HEIGHT + 80:
                    self.projectiles_queue.pop(0)
                    if not self.projectiles_queue: self.end_turn_cycle()
                    return

                if 0 <= int(proj.x) < WIDTH:
                    if proj.y >= self.terrain.heights[int(proj.x)]:
                        self.trigger_explosion(proj.x, proj.y, proj.profile, proj.owner)
                        return

                for target in self.tanks:
                    if math.hypot(proj.x - target.x, proj.y - (target.y - 10)) < 19.0:
                        self.trigger_explosion(proj.x, proj.y, proj.profile, proj.owner)
                        return

        elif self.substate == Game.SUBSTATE_EXPLODING:
            if self.current_explosion:
                self.current_explosion.update()
                if self.current_explosion.is_finished:
                    self.current_explosion = None
                    if self.projectiles_queue: self.projectiles_queue.pop(0)

                    if self.projectiles_queue: self.substate = Game.SUBSTATE_FIRING
                    else: self.end_turn_cycle()

        # MONITOREO DE GRAVEDAD Y CAÍDA LIBRE PARA TODOS LOS TANQUES EN CADA FRAME
        for t in self.tanks:
            t.update_position(self.terrain)
            if t.y >= HEIGHT - 5:  # Caída fuera de la pantalla automática = muerte instantánea
                t.health = 0

        # EVALUACIÓN CONTINUA DE CONDICIÓN DE VICTORIA (QA MONITOR)
        p1_alive = self.player1.health > 0
        p2_alive = self.player2.health > 0
        if not p1_alive or not p2_alive:
            if not p1_alive and not p2_alive: self.winner_name = "Empate Táctico"
            else: self.winner_name = self.player2.name if not p1_alive else self.player1.name
            self.state = Game.STATE_GAME_OVER

    def trigger_explosion(self, x, y, profile, owner):
        if self.snd_explosion: self.snd_explosion.play()

        radius = profile.radius
        v_shift = 25 if profile.special_type == "buster" else 0
        
        mined_gold = self.terrain.destroy(x, y, radius, vertical_shift=v_shift)
        owner.gold += mined_gold

        # DAÑO RADIAL MATEMÁTICO CON ATENUACIÓN LINEAL DIRECTA
        for target in self.tanks:
            distance = math.hypot(target.x - x, (target.y - 10) - (y + v_shift))
            if distance < radius:
                factor = 1.0 - (distance / radius)
                calculated_dmg = int(profile.damage * factor * owner.next_damage_mult)
                
                if calculated_dmg < 6 and factor > 0.0: calculated_dmg = 6

                if target.shield > 0:
                    if target.shield >= calculated_dmg:
                        target.shield -= calculated_dmg
                        calculated_dmg = 0
                    else:
                        calculated_dmg -= target.shield
                        target.shield = 0
                
                target.health -= calculated_dmg
                if target != owner and calculated_dmg > 0:
                    owner.gold += int(calculated_dmg * 1.5)

        owner.next_damage_mult = 1.0
        for t in self.tanks: t.update_position(self.terrain)

        self.current_explosion = ExplosionAnimation(x, y + v_shift, radius)
        p_color = (120, 200, 255) if profile.special_type == "thunder" else (243, 156, 18)
        num_particles = 55 if radius > 60 else 26
        
        for _ in range(num_particles):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(1.8, 6.0)
            self.particles.append(Particle(x, y + v_shift, p_color, math.cos(ang)*spd, math.sin(ang)*spd - 1.5))

        if profile.special_type == "thunder":
            for ty in range(0, int(y), 14):
                self.particles.append(Particle(x + random.uniform(-4, 4), ty, (173, 232, 244), 0, random.uniform(1, 3)))

        self.substate = Game.SUBSTATE_EXPLODING

    def end_turn_cycle(self):
        self.projectiles_queue.clear()
        self.current_explosion = None
        self.current_turn = (self.current_turn + 1) % 2
        self.turn_timer = 30.0
        self.randomize_wind()
        self.substate = Game.SUBSTATE_AIMING

    def draw_aiming_radar(self, surface):
        """Radar de guía acotada: Ajusta su aguja e indicadores al ángulo absoluto real."""
        player = self.get_current_player()
        
        # ÁNGULO ABSOLUTO INTEGRADO (Suelo + Cañón)
        abs_angle = player.base_angle + player.angle
        rad = math.radians(abs_angle)
        
        cx = int(player.x)
        cy = int(player.y - 12)
        
        if self.substate == Game.SUBSTATE_CHARGING:
            ratio = player.power / 100.0
            r = int(46 * (1 - ratio) + 231 * ratio)
            g = int(204 * (1 - ratio) + 76 * ratio)
            b = int(113 * (1 - ratio) + 60 * ratio)
            dots_color = (r, g, b)
        else:
            dots_color = (46, 204, 113)

        radius_start = 28
        radius_end = 45
        
        # AGUJA CENTRAL EN ROJO INTENSO (Calculada de forma absoluta)
        p_start_x = cx + math.cos(rad) * radius_start
        p_start_y = cy - math.sin(rad) * radius_start
        p_end_x = cx + math.cos(rad) * radius_end
        p_end_y = cy - math.sin(rad) * radius_end
        pygame.draw.line(surface, (231, 76, 60), (int(p_start_x), int(p_start_y)), (int(p_end_x), int(p_end_y)), 3)
        
        # Arcos complementarios rotados solidariamente
        for offset_deg in [-15, -7.5, 7.5, 15]:
            rad_off = math.radians(abs_angle + offset_deg)
            pt_x = cx + math.cos(rad_off) * radius_end
            pt_y = cy - math.sin(rad_off) * radius_end
            pygame.draw.circle(surface, dots_color, (int(pt_x), int(pt_y)), 2)

    def draw_beautiful_gradient(self):
        for y in range(0, HEIGHT, 4):
            ratio = y / HEIGHT
            if ratio < 0.5:
                lr = ratio * 2.0
                r = int(COLOR_SKY_TOP[0]*(1-lr) + COLOR_SKY_MID[0]*lr)
                g = int(COLOR_SKY_TOP[1]*(1-lr) + COLOR_SKY_MID[1]*lr)
                b = int(COLOR_SKY_TOP[2]*(1-lr) + COLOR_SKY_MID[2]*lr)
            else:
                lr = (ratio - 0.5) * 2.0
                r = int(COLOR_SKY_MID[0]*(1-lr) + COLOR_SKY_BOTTOM[0]*lr)
                g = int(COLOR_SKY_MID[1]*(1-lr) + COLOR_SKY_BOTTOM[1]*lr)
                b = int(COLOR_SKY_MID[2]*(1-lr) + COLOR_SKY_BOTTOM[2]*lr)
            pygame.draw.rect(self.screen, (r, g, b), (0, y, WIDTH, 4))

    def draw_power_bar(self, surface):
        p = self.get_current_player()
        bx = WIDTH // 2 - 250
        by = HEIGHT - 45
        bw = 500
        bh = 22
        
        pygame.draw.rect(surface, (30, 30, 30), (bx, by, bw, bh), border_radius=2)
        pygame.draw.rect(surface, (150, 150, 150), (bx, by, bw, bh), 2, border_radius=2)
        
        fill_w = int(bw * (p.power / 100.0))
        if fill_w > 0:
            power_surf = pygame.Surface((fill_w, bh - 4))
            power_surf.fill((241, 196, 15) if p.power < 75 else (231, 76, 60))
            surface.blit(power_surf, (bx + 2, by + 2))
            
        for i in range(1, 10):
            seg_x = bx + int(bw * (i / 10.0))
            pygame.draw.line(surface, (100, 100, 100), (seg_x, by), (seg_x, by + bh - 1), 1)

        txt_p = self.font_sm.render(f"FORCE: {p.power:.1f}%", True, COLOR_WHITE)
        surface.blit(txt_p, (bx + bw // 2 - txt_p.get_width() // 2, by - 18))

    def draw_shop_overlay(self, surface):
        overlay = pygame.Surface((520, 300), pygame.SRCALPHA)
        overlay.fill((15, 15, 25, 235))
        pygame.draw.rect(overlay, COLOR_GOLD, (0, 0, 520, 300), 2, border_radius=4)
        p = self.get_current_player()
        
        t_title = self.font_title.render("TIENDA TÁCTICA", True, COLOR_GOLD)
        overlay.blit(pygame.transform.scale(t_title, (320, 32)), (100, 20))
        
        items = [
            ("1. Escudo de Energía Absorbente (+25 SHIELD)", "100G"),
            ("2. Nano-Kit de Reparación Estructura (+30 HP)", "120G"),
            ("3. Módulo de Sobrecarga Atómica (Próximo shot x1.5)", "150G")
        ]
        y_off = 85
        for desc, cost in items:
            overlay.blit(self.font_main.render(desc, True, COLOR_WHITE), (30, y_off))
            overlay.blit(self.font_main.render(cost, True, COLOR_GOLD), (440, y_off))
            y_off += 45
        overlay.blit(self.font_sm.render("Presione [T] o [ESC] para salir del suministro comercial.", True, (170, 170, 170)), (30, 250))
        surface.blit(overlay, (WIDTH // 2 - 260, HEIGHT // 2 - 150))

    def render_character_select_screen(self):
        title = self.font_title.render("SELECCIÓN DE COMPAÑÍA MÓVIL", True, COLOR_GOLD)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        
        phase_str = "JUGADOR 1: Seleccione su Unidad" if self.selection_phase == 1 else "JUGADOR 2: Seleccione su Unidad"
        t_phase = self.font_main.render(phase_str, True, COLOR_WHITE)
        self.screen.blit(t_phase, (WIDTH // 2 - t_phase.get_width() // 2, 110))

        card_w, card_h = 190, 260
        start_x = WIDTH // 2 - (card_w * 4 + 30 * 3) // 2
        y_pos = 180

        map_names = {1: "Colinas Suaves", 2: "Montañas Altas", 3: "Valles Profundos", 4: "Ondas Regulares", 5: "Mesetas / Terrazas"}
        t_map = self.font_main.render(f"Mapa seleccionado para la batalla: {map_names[self.terrain.map_type].upper()}", True, (52, 152, 219))
        self.screen.blit(t_map, (WIDTH // 2 - t_map.get_width() // 2, HEIGHT - 150))

        for i, m_type in enumerate(self.mobiles_pool):
            cx = start_x + i * (card_w + 30)
            
            is_hovered = (self.selection_phase == 1 and self.p1_sel_idx == i) or (self.selection_phase == 2 and self.p2_sel_idx == i)
            border_color = COLOR_GOLD if is_hovered else (70, 85, 110)
            bg_color = (25, 35, 60) if is_hovered else (15, 20, 35)
            
            pygame.draw.rect(self.screen, bg_color, (cx, y_pos, card_w, card_h), border_radius=6)
            pygame.draw.rect(self.screen, border_color, (cx, y_pos, card_w, card_h), 3, border_radius=6)
            
            preview_x = cx + card_w // 2
            preview_y = y_pos + 120
            
            if self.asset_mgr.use_sprites:
                spr = self.asset_mgr.sprites[m_type]['idle']
                rect_spr = spr.get_rect(center=(preview_x, preview_y))
                self.screen.blit(spr, rect_spr.topleft)
            else:
                if m_type == 'Knight':
                    pygame.draw.rect(self.screen, (41, 128, 185), (preview_x - 20, preview_y - 10, 40, 12), border_radius=3)
                    pygame.draw.polygon(self.screen, (52, 152, 219), [(preview_x - 8, preview_y - 10), (preview_x + 8, preview_y - 10), (preview_x, preview_y - 22)])
                elif m_type == 'Mage':
                    pygame.draw.polygon(self.screen, (192, 41, 43), [(preview_x - 18, preview_y), (preview_x + 18, preview_y), (preview_x, preview_y - 16)])
                    pygame.draw.circle(self.screen, (155, 89, 182), (preview_x, preview_y - 22), 6)
                elif m_type == 'Dragon':
                    pygame.draw.rect(self.screen, (39, 174, 96), (preview_x - 18, preview_y - 10, 36, 11), border_radius=4)
                    pygame.draw.polygon(self.screen, COLOR_WHITE, [(preview_x - 2, preview_y - 10), (preview_x - 12, preview_y - 24), (preview_x + 4, preview_y - 10)])
                elif m_type == 'Heavy':
                    pygame.draw.rect(self.screen, (127, 140, 141), (preview_x - 24, preview_y - 4, 48, 6))
                    pygame.draw.rect(self.screen, (211, 84, 0), (preview_x - 18, preview_y - 15, 36, 11))
                
            t_name = self.font_main.render(m_type, True, COLOR_WHITE)
            self.screen.blit(t_name, (cx + card_w//2 - t_name.get_width()//2, y_pos + 20))
            
            hp_label = "HP: 135 (Alto)" if m_type == 'Heavy' else "HP: 100 (Normal)"
            t_desc = self.font_sm.render(hp_label, True, (160, 170, 190))
            self.screen.blit(t_desc, (cx + card_w//2 - t_desc.get_width()//2, y_pos + 210))

        t_footer = self.font_sm.render("Use [FLECHAS] para navegar | [ENTER / ESPACIO] para confirmar unidad", True, COLOR_GOLD)
        self.screen.blit(t_footer, (WIDTH // 2 - t_footer.get_width() // 2, HEIGHT - 90))

    def render(self):
        self.draw_beautiful_gradient()
        for p in self.particles: p.draw(self.screen)

        if self.state == Game.STATE_MENU:
            t_m = self.font_title.render("HASTA EL ULTIMO CARTUCHO", True, COLOR_GOLD)
            t_s = self.font_main.render("Presione [ESPACIO] para ingresar al hangar estratégico", True, COLOR_WHITE)
            self.screen.blit(t_m, (WIDTH//2 - t_m.get_width()//2, HEIGHT//2 - 50))
            self.screen.blit(t_s, (WIDTH//2 - t_s.get_width()//2, HEIGHT//2 + 25))

        elif self.state == Game.STATE_CHARACTER_SELECT:
            self.render_character_select_screen()

        elif self.state == Game.STATE_PLAYING:
            self.terrain.draw(self.screen) 
            self.player1.draw(self.screen, self.current_turn == 0, self.asset_mgr)
            self.player2.draw(self.screen, self.current_turn == 1, self.asset_mgr)

            if self.substate in [Game.SUBSTATE_AIMING, Game.SUBSTATE_CHARGING]:
                self.draw_aiming_radar(self.screen)
                
            if self.substate == Game.SUBSTATE_FIRING and self.projectiles_queue:
                self.projectiles_queue[0].draw(self.screen)
                
            if self.substate == Game.SUBSTATE_EXPLODING and self.current_explosion:
                self.current_explosion.draw(self.screen)

            # CONTROL DE PANEL SUPERIOR (HUD)
            panel = pygame.Surface((WIDTH, 65), pygame.SRCALPHA)
            panel.fill((16, 22, 33, 210))
            self.screen.blit(panel, (0, 0))

            cp = self.get_current_player()
            weapons_list = CHARACTER_WEAPONS[cp.mobile_type]
            cw = weapons_list[self.current_weapon_idx[self.current_turn]]

            w_dir = "Derecha >>" if self.wind_x >= 0 else "<< Izquierda"
            self.screen.blit(self.font_main.render(f"TURNO: {cp.name} ({cp.mobile_type})", True, cp.color), (30, 10))
            self.screen.blit(self.font_main.render(f"VIENTO: {abs(self.wind_x):.2f} {w_dir}", True, (52, 152, 219)), (30, 36))
            self.screen.blit(self.font_main.render(f"TIME: {max(0.0, self.turn_timer):.1f}s", True, COLOR_WHITE), (320, 20))
            self.screen.blit(self.font_main.render(f"ORO: {cp.gold}G", True, COLOR_GOLD), (490, 20))

            self.screen.blit(self.font_main.render(f"ARMA [{self.current_weapon_idx[self.current_turn]+1}]: {cw.name} (Coste: {cw.cost}G)", True, COLOR_BULLET), (655, 10))
            self.screen.blit(self.font_sm.render(f"{cw.desc} Seleccione con teclas [1-5]", True, (180, 185, 195)), (655, 38))

            self.draw_power_bar(self.screen)

            if self.substate == Game.SUBSTATE_SHOP:
                self.draw_shop_overlay(self.screen)

        elif self.state == Game.STATE_GAME_OVER:
            t_g = self.font_title.render("COMBATE FINALIZADO", True, COLOR_GOLD)
            t_v = self.font_main.render(f"Ganador de la ronda de simulación: {self.winner_name}", True, COLOR_WHITE)
            t_r = self.font_sm.render("Presione [R] para reiniciar al hangar de selección o [ESC] para el menú.", True, COLOR_WHITE)
            self.screen.blit(t_g, (WIDTH//2 - t_g.get_width()//2, HEIGHT//3))
            self.screen.blit(t_v, (WIDTH//2 - t_v.get_width()//2, HEIGHT//3 + 70))
            self.screen.blit(t_r, (WIDTH//2 - t_r.get_width()//2, HEIGHT//3 + 140))

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update_physics_and_logic()
            self.render()
            self.clock.tick(FPS)


# ==============================================================================
# PUNTO DE ENTRADA AL COMPILADO DE TESTING Y DESPLIEGUE SEGURO
# ==============================================================================
if __name__ == "__main__":
    game_instance = Game()
    game_instance.run()

# === VERSIÓN FINAL 6 - Rotación del Tanque según Inclinación del Terreno + Cañón Relativo - Para curso de Testing ===