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

# ── Helpers ───────────────────────────────────────────────────────────────────
def draw_gradient_bg(surface):
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
 
 
def draw_egg(surface, x, y, color, shine=True):
    """Draw a nice ellipse egg with a shine dot."""
    pygame.draw.ellipse(surface, color,
                        (x - EGG_RX, y - EGG_RY, EGG_RX * 2, EGG_RY * 2))



    # dark outline
    pygame.draw.ellipse(surface, (max(color[0]-60,0), max(color[1]-60,0), max(color[2]-60,0)),
                        (x - EGG_RX, y - EGG_RY, EGG_RX * 2, EGG_RY * 2), 2)
    if shine:
        pygame.draw.ellipse(surface, (255, 255, 255, 180),
                            (x - EGG_RX + 5, y - EGG_RY + 5, 8, 6))


def draw_basket(surface, x, y):
    """Draw a simple basket shape."""
    bx = x - BASKET_W // 2
    # body
    pts = [
        (bx, y),
        (bx + BASKET_W, y),
        (bx + BASKET_W - 10, y + BASKET_H),
        (bx + 10, y + BASKET_H),
    ]
    pygame.draw.polygon(surface, ORANGE, pts)
    pygame.draw.polygon(surface, (200, 100, 0), pts, 3)
    # rim
    pygame.draw.rect(surface, YELLOW, (bx - 4, y - 6, BASKET_W + 8, 10), border_radius=5)
    pygame.draw.rect(surface, GOLD,   (bx - 4, y - 6, BASKET_W + 8, 10), 2, border_radius=5)
    # weave lines
    for i in range(1, 4):
        lx = bx + i * (BASKET_W // 4)
        pygame.draw.line(surface, (180, 90, 0), (lx, y), (lx - 5, y + BASKET_H), 2)
 
 
def draw_star(surface, cx, cy, r, color):
    import math
    pts = []
    for i in range(10):
        angle = math.radians(i * 36 - 90)
        radius = r if i % 2 == 0 else r // 2
        pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    pygame.draw.polygon(surface, color, pts)

# ── Egg class ─────────────────────────────────────────────────────────────────
EGG_COLOURS = [YELLOW, WHITE, GREEN, BLUE, PURPLE, RED, ORANGE]
 
class Egg:
    def __init__(self, speed):
        self.x = random.randint(EGG_RX + 10, WIDTH - EGG_RX - 10)
        self.y = -EGG_RY
        self.speed = speed + random.uniform(-0.5, 0.5)
        self.color = random.choice(EGG_COLOURS)
        # golden egg: rare, worth 5 pts
        self.golden = random.random() < 0.08
        if self.golden:
            self.color = GOLD
    def update(self):
        self.y += self.speed
 
    def draw(self, surface):
        draw_egg(surface, self.x, self.y, self.color)
        if self.golden:
            draw_star(surface, self.x, self.y - EGG_RY - 8, 6, GOLD)
 
    def caught(self, bx):
        """Returns True if the egg overlaps the basket top."""
        return (abs(self.x - bx) < BASKET_W // 2 + EGG_RX - 5 and
                abs(self.y - BASKET_Y) < EGG_RY + 10)
 
    def missed(self):
        return self.y - EGG_RY > HEIGHT

# ── Particle class ────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.life = 30
 
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 1
 
    def draw(self, surface):
        alpha = max(0, self.life / 30)
        r = int(self.color[0] * alpha)
        g = int(self.color[1] * alpha)
        b = int(self.color[2] * alpha)
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), 4)
 
 # ── Global basket Y                                    