# ==============================================================================
# ORQUESTADOR CENTRAL DE FLUJO Y MÁQUINA DE ESTADOS (MÓDULO PRINCIPAL)
# ==============================================================================

import pygame
import math
import random
import sys

# Importación estratégica modularizada
from constants import *
from utils import AssetManager, SoundGenerator
from weapons import CHARACTER_WEAPONS
from effects import Particle, ExplosionAnimation
from entities import Tank, Projectile
from terrain import Terrain

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
        pygame.display.set_caption("Hasta el Último Cartucho - Remaster Modular")
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

        for t in self.tanks:
            t.update_position(self.terrain)
            if t.y >= HEIGHT - 5:  
                t.health = 0

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
        player = self.get_current_player()
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
        
        p_start_x = cx + math.cos(rad) * radius_start
        p_start_y = cy - math.sin(rad) * radius_start
        p_end_x = cx + math.cos(rad) * radius_end
        p_end_y = cy - math.sin(rad) * radius_end
        pygame.draw.line(surface, (231, 76, 60), (int(p_start_x), int(p_start_y)), (int(p_end_x), int(p_end_y)), 3)
        
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
            t_m = self.font_title.render("HASTA EL ÚLTIMO CARTUCHO", True, COLOR_GOLD)
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

if __name__ == "__main__":
    game_instance = Game()
    game_instance.run()

# === VERSIÓN FINAL 6 - Rotación del Tanque según Inclinación del Terreno + Cañón Relativo - Para curso de Testing ===