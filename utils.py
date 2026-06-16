# ==============================================================================
# MÓDULO: SISTEMAS AUXILIARES Y UTILITARIOS
# ==============================================================================

import pygame
import os
import math
import array
import random

class AssetManager:
    """Carga y administra los recursos gráficos implementando tolerancia a fallos."""
    def __init__(self):
        self.use_sprites = True
        self.sprites = {}
        self.load_all_assets()

    def safe_load(self, path, scale_dims=None):
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


class SoundGenerator:
    """Generador procedimental de ondas sinusoidales binarias de audio PCM."""
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