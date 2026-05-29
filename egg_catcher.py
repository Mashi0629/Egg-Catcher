import pygame
import random
import sys

# Initialize Pygame
pygame.init()   

# ── Constants ─────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 600, 700
FPS = 60

# Colours
BG_TOP       = (20, 20, 50)
BG_BOTTOM    = (10, 10, 30)
WHITE        = (255, 255, 255)
YELLOW       = (255, 220, 50)
ORANGE       = (255, 140, 0)
RED          = (220, 60, 60)
GREEN        = (60, 200, 100)
BLUE         = (80, 140, 255)
GRAY         = (160, 160, 160)
DARK         = (30, 30, 60)
GOLD         = (255, 200, 0)
PURPLE       = (160, 80, 220)

# Game settings per level
LEVEL_SETTINGS = {
    1: {"speed": 3,  "spawn_rate": 80,  "eggs_to_next": 10, "label": "Easy"},
    2: {"speed": 5,  "spawn_rate": 60,  "eggs_to_next": 20, "label": "Medium"},
    3: {"speed": 7,  "spawn_rate": 45,  "eggs_to_next": 30, "label": "Hard"},
    4: {"speed": 9,  "spawn_rate": 30,  "eggs_to_next": 40, "label": "Expert"},
    5: {"speed": 11, "spawn_rate": 20,  "eggs_to_next": 50, "label": "Insane"},
}
MAX_LEVEL = 5
MAX_LIVES = 5
BASKET_W, BASKET_H = 100, 28
EGG_RX, EGG_RY = 18, 22   # egg radii

