# ==============================================================================
# MÓDULO: ENTIDADES CINEMÁTICAS ACTIVAS (CON LÍMITE DE COMBUSTIBLE)
# ==============================================================================

import pygame
import math
from constants import WIDTH, HEIGHT, COLOR_WHITE

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
        
        # --- SISTEMA DE COMBUSTIBLE ENERGÉTICO ---
        self.max_fuel = 100.0
        self.fuel = self.max_fuel
        
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
        ix = max(0, min(int(self.x), WIDTH - 1))
        if self.y < float(terrain.heights[ix]):
            return 0.0
            
        x_left = max(0, min(int(self.x - 14), WIDTH - 1))
        x_right = max(0, min(int(self.x + 14), WIDTH - 1))
        
        y_left = terrain.heights[x_left]
        y_right = terrain.heights[x_right]
        
        dx = x_right - x_left
        dy = y_right - y_left  
        
        if dx == 0: return 0.0
        
        target_angle = math.degrees(math.atan2(-dy, dx))
        return max(-35.0, min(target_angle, 35.0))

    def update_position(self, terrain):
        ix = max(0, min(int(self.x), WIDTH - 1))
        ground_y = float(terrain.heights[ix])
        
        if self.y < ground_y:
            self.vy += 0.38  
            self.y += self.vy
            if self.y >= ground_y:
                self.y = ground_y
                self.vy = 0.0
        else:
            self.y = ground_y
            self.vy = 0.0
            
        target_slope = self.calculate_terrain_slope(terrain)
        self.base_angle += (target_slope - self.base_angle) * 0.15

        if self.recoil_offset > 0: self.recoil_offset -= 0.6
        if self.muzzle_flash_frames > 0: self.muzzle_flash_frames -= 1

    def move(self, direction, terrain):
        """Desplaza al tanque consumiendo combustible de manera lineal."""
        if self.fuel <= 0:
            self.is_moving = False
            return  # Bloqueo absoluto de motricidad por falta de energía

        # Consumo de combustible proporcional a la velocidad y tasa de gasto
        fuel_cost = abs(direction * self.speed) * 0.45
        self.fuel = max(0.0, self.fuel - fuel_cost)

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
        
        rad_recoil = math.radians(self.base_angle + self.angle)
        draw_x = tx - int(math.cos(rad_recoil) * self.recoil_offset)
        draw_y = ty + int(math.sin(rad_recoil) * self.recoil_offset)

        pivot_x = draw_x
        pivot_y = draw_y - 12

        abs_angle = self.base_angle + self.angle
        abs_rad = math.radians(abs_angle)
        barrel_len = 24
        bx = pivot_x + math.cos(abs_rad) * barrel_len
        by = pivot_y - math.sin(abs_rad) * barrel_len

        # 1. RENDERIZADO DEL CAÑÓN
        if asset_mgr.use_sprites:
            orig_cannon = asset_mgr.sprites[self.mobile_type]['cannon']
            rotated_cannon = pygame.transform.rotate(orig_cannon, abs_angle)
            rot_rect = rotated_cannon.get_rect()
            rot_rect.center = (pivot_x + math.cos(abs_rad) * (barrel_len / 2), pivot_y - math.sin(abs_rad) * (barrel_len / 2))
            surface.blit(rotated_cannon, rot_rect.topleft)
        else:
            pygame.draw.line(surface, (236, 240, 241), (pivot_x, pivot_y), (int(bx), int(by)), 4)

        # 2. RENDERIZADO DEL CHASIS
        if asset_mgr.use_sprites:
            if not self.is_moving:
                frame_sprite = asset_mgr.sprites[self.mobile_type]['idle']
            else:
                frame_sprite = asset_mgr.sprites[self.mobile_type]['move1'] if self.anim_toggle else asset_mgr.sprites[self.mobile_type]['move2']
            
            rotated_body = pygame.transform.rotate(frame_sprite, self.base_angle)
            body_rect = rotated_body.get_rect(center=(draw_x, draw_y - 10))
            surface.blit(rotated_body, body_rect.topleft)
        else:
            cx, cy = draw_x, draw_y - 10
            p1 = self.rotate_point_helper(cx, cy, draw_x - 18, draw_y - 16, self.base_angle)
            p2 = self.rotate_point_helper(cx, cy, draw_x + 18, draw_y - 16, self.base_angle)
            p3 = self.rotate_point_helper(cx, cy, draw_x + 18, draw_y - 6, self.base_angle)
            p4 = self.rotate_point_helper(cx, cy, draw_x - 18, draw_y - 6, self.base_angle)
            pygame.draw.polygon(surface, self.color, [p1, p2, p3, p4])

            for wx in [-14, -5, 5, 14]:
                w_cx, w_cy = self.rotate_point_helper(cx, cy, draw_x + wx, draw_y - 4, self.base_angle)
                pygame.draw.circle(surface, (44, 62, 80), (w_cx, w_cy), 5)

        # 3. RENDERIZADO DEL MUZZLE FLASH
        if self.muzzle_flash_frames > 0:
            if asset_mgr.use_sprites and asset_mgr.sprites['muzzle_flash']:
                mf_sprite = asset_mgr.sprites['muzzle_flash']
                rotated_mf = pygame.transform.rotate(mf_sprite, abs_angle)
                mf_rect = rotated_mf.get_rect(center=(int(bx), int(by)))
                surface.blit(rotated_mf, mf_rect.topleft)
            else:
                pygame.draw.circle(surface, (254, 202, 87), (int(bx), int(by)), 9)
                pygame.draw.circle(surface, COLOR_WHITE, (int(bx), int(by)), 5)

        # 4. ELEMENTOS ESTÁTICOS DE INTERFAZ INTEGRADA (HP / SHIELD / FUEL)
        bar_w = 46
        bx_pos = draw_x - bar_w // 2
        by_pos = draw_y - 46
        
        # Render de Barra de Salud (Verde)
        pygame.draw.rect(surface, (50, 50, 50), (bx_pos, by_pos, bar_w, 4))
        hp_ratio = max(0.0, min(1.0, self.health / self.max_health))
        pygame.draw.rect(surface, (46, 204, 113), (bx_pos, by_pos, int(bar_w * hp_ratio), 4))
        
        # Render de Barra de Escudo si está activo (Celeste)
        if self.shield > 0:
            sh_ratio = max(0.0, min(1.0, self.shield / 50.0))
            pygame.draw.rect(surface, (52, 152, 219), (bx_pos, by_pos + 5, int(bar_w * sh_ratio), 3))
            by_pos += 4
            
        # Render de Barra de Combustible Flotante (Amarilla/Oro)
        pygame.draw.rect(surface, (50, 50, 50), (bx_pos, by_pos + 5, bar_w, 3))
        fuel_ratio = max(0.0, min(1.0, self.fuel / self.max_fuel))
        pygame.draw.rect(surface, (254, 211, 48), (bx_pos, by_pos + 5, int(bar_w * fuel_ratio), 3))

        font_tag = pygame.font.SysFont("Arial", 11, bold=True)
        txt_name = font_tag.render(self.name, True, COLOR_WHITE)
        surface.blit(txt_name, (draw_x - txt_name.get_width() // 2, by_pos - 15))


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
        from constants import COLOR_EXPLOSION, COLOR_BULLET
        color = (235, 94, 40) if self.profile.special_type == "thunder" else COLOR_BULLET
        radius = 6 if self.profile.radius > 60 else 3
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)