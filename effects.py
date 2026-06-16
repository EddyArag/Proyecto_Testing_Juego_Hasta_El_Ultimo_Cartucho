# ==============================================================================
# MÓDULO: MOTOR DE RENDERIZADO DE EFECTOS ESPECIALES
# ==============================================================================

import pygame
import math
import random

class Particle:
    """Simula una chispa o ráfaga de metralla con decaimiento alfa progresivo."""
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


class ExplosionAnimation:
    """Dibuja una esfera expansiva simulando la disipación térmica de plasma."""
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