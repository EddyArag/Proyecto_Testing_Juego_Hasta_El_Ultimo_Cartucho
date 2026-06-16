# ==============================================================================
# MÓDULO: MOTOR MAPA DE RELIEVE TOPOGRÁFICO
# ==============================================================================

import pygame
import math
import random
from constants import COLOR_TERRAIN, COLOR_TERRAIN_SUB

class Terrain:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.heights = []
        self.map_type = random.randint(1, 5)  
        self.generate_procedural_terrain()

    def generate_procedural_terrain(self):
        self.heights.clear()
        
        if self.map_type == 1:
            base_level = self.height * 0.75
            for x in range(self.width):
                h = base_level + math.sin(x * 0.004) * 35 + math.sin(x * 0.012) * 10
                self.heights.append(int(max(self.height * 0.35, min(h, self.height * 0.92))))
                
        elif self.map_type == 2:
            base_level = self.height * 0.60
            for x in range(self.width):
                h = base_level + math.sin(x * 0.006) * 165 + math.cos(x * 0.022) * 45
                self.heights.append(int(max(self.height * 0.25, min(h, self.height * 0.92))))
                
        elif self.map_type == 3:
            base_level = self.height * 0.52
            for x in range(self.width):
                h = base_level + math.sin(x * 0.003) * 150 + math.sin(x * 0.0015) * 95
                self.heights.append(int(max(self.height * 0.28, min(h, self.height * 0.92))))
                
        elif self.map_type == 4:
            base_level = self.height * 0.70
            for x in range(self.width):
                h = base_level + math.sin(x * 0.032) * 55 + math.sin(x * 0.016) * 20
                self.heights.append(int(max(self.height * 0.35, min(h, self.height * 0.92))))
                
        else:
            base_level = self.height * 0.65
            for x in range(self.width):
                steps = int(math.sin(x * 0.0055) * 4) * 38
                smooth_blend = math.sin(x * 0.02) * 8
                h = base_level + steps + smooth_blend
                self.heights.append(int(max(self.height * 0.32, min(h, self.height * 0.92))))

    def destroy(self, center_x, center_y, radius, vertical_shift=0):
        cx, cy = int(center_x), int(center_y) + int(vertical_shift)
        r = int(radius)
        start_x = max(0, cx - r)
        end_x = min(self.width, cx + r + 1)
        gold_gained = 0

        for x in range(start_x, end_x):
            dx = x - cx
            chord = math.sqrt(r**2 - dx**2)
            circle_bottom = cy + chord + int(math.sin(x * 0.4) * 4.0)

            if self.heights[x] < circle_bottom:
                diff = int(circle_bottom - self.heights[x])
                gold_gained += min(diff, 8)
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