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

 BASKET_Y = HEIGHT - 80 

# ── Game states ───────────────────────────────────────────────────────────────
STATE_MENU    = "menu"
STATE_PLAYING = "playing"
STATE_LEVEL_UP = "level_up"
STATE_GAME_OVER = "game_over"
STATE_WIN     = "win"

# ── Main game ─────────────────────────────────────────────────────────────────
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🥚 Egg Catcher")
    clock = pygame.time.Clock()
 
    font_big   = pygame.font.SysFont("Arial", 52, bold=True)
    font_med   = pygame.font.SysFont("Arial", 32, bold=True)
    font_small = pygame.font.SysFont("Arial", 22)
    font_tiny  = pygame.font.SysFont("Arial", 18)
 
    def txt(text, font, color, cx, cy, shadow=True):
        if shadow:
            s = font.render(text, True, (0, 0, 0))
            screen.blit(s, s.get_rect(center=(cx + 2, cy + 2)))
        surf = font.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=(cx, cy)))


    # ── Game variables ────────────────────────────────────────────────────────
    def reset_game():
        return {
            "state": STATE_MENU,
            "score": 0,
            "lives": MAX_LIVES,
            "level": 1,
            "eggs_caught": 0,
            "basket_x": WIDTH // 2,
            "eggs": [],
            "particles": [],
            "spawn_timer": 0,
            "flash": 0,
            "high_score": 0,
        }
    g = reset_game()
    high_score = 0
 
    running = True
    while running:
        clock.tick(FPS)
        draw_gradient_bg(screen)


# ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
 
                if g["state"] == STATE_MENU:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        g["state"] = STATE_PLAYING
 
                elif g["state"] in (STATE_GAME_OVER, STATE_WIN):
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        high_score = max(high_score, g["score"])
                        g = reset_game()
                        g["state"] = STATE_MENU
 
                elif g["state"] == STATE_LEVEL_UP:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        g["state"] = STATE_PLAYING

# ── MENU ──────────────────────────────────────────────────────────────
        if g["state"] == STATE_MENU:
            txt("🥚 EGG CATCHER", font_big, YELLOW, WIDTH // 2, 160)
            txt("Catch the falling eggs!", font_small, WHITE, WIDTH // 2, 240)
            txt("← → Arrow Keys  to move basket", font_small, GRAY, WIDTH // 2, 290)
            txt("Golden eggs  ★  are worth 5 pts!", font_small, GOLD, WIDTH // 2, 335)
            txt(f"High Score: {high_score}", font_med, GREEN, WIDTH // 2, 400)

# blinking start prompt
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                txt("Press SPACE to Start", font_med, WHITE, WIDTH // 2, 470)

# draw demo eggs
            for i, col in enumerate([YELLOW, WHITE, GREEN, BLUE, PURPLE]):
                draw_egg(screen, 80 + i * 110, 570, col)
            draw_basket(screen, WIDTH // 2, 620)                  

        # ── PLAYING ───────────────────────────────────────────────────────────
        elif g["state"] == STATE_PLAYING:
            cfg = LEVEL_SETTINGS[g["level"]]
 
            # Basket movement
            keys = pygame.key.get_pressed()
            speed_px = 7
            if keys[pygame.K_LEFT]:
                g["basket_x"] = max(BASKET_W // 2 + 4, g["basket_x"] - speed_px)
            if keys[pygame.K_RIGHT]:
                g["basket_x"] = min(WIDTH - BASKET_W // 2 - 4, g["basket_x"] + speed_px)
 
             # Spawn eggs
            g["spawn_timer"] += 1
            if g["spawn_timer"] >= cfg["spawn_rate"]:
                g["spawn_timer"] = 0
                g["eggs"].append(Egg(cfg["speed"]))
 
            # Update eggs
            caught_this_frame = []
            missed_this_frame = []
            for egg in g["eggs"]:
                egg.update()
                if egg.caught(g["basket_x"]):
                    caught_this_frame.append(egg)
                elif egg.missed():
                    missed_this_frame.append(egg)
 
            for egg in caught_this_frame:
                g["eggs"].remove(egg)
                pts = 5 if egg.golden else 1
                g["score"] += pts
                g["eggs_caught"] += pts if not egg.golden else 5
                g["flash"] = 8
                for _ in range(12):
                    g["particles"].append(Particle(egg.x, BASKET_Y, egg.color))
 
            for egg in missed_this_frame:
                g["eggs"].remove(egg)
                g["lives"] -= 1
                g["flash"] = -8   # red flash
                for _ in range(8):
                    g["particles"].append(Particle(egg.x, HEIGHT - 5, RED))
 
            # Particles
            g["particles"] = [p for p in g["particles"] if p.life > 0]
            for p in g["particles"]:
                p.update()
                p.draw(screen)

            # Level up check
            if g["eggs_caught"] >= cfg["eggs_to_next"]:
                g["eggs_caught"] = 0
                g["eggs"] = []
                if g["level"] >= MAX_LEVEL:
                    g["state"] = STATE_WIN
                else:
                    g["level"] += 1
                    g["state"] = STATE_LEVEL_UP

                        # Lives check
            if g["lives"] <= 0:
                g["state"] = STATE_GAME_OVER
 
            # Draw eggs
            for egg in g["eggs"]:
                egg.draw(screen)
 
            # Draw basket
            draw_basket(screen, g["basket_x"], BASKET_Y)
 
            # Flash overlay
            if g["flash"] > 0:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((255, 255, 100, int(80 * g["flash"] / 8)))
                screen.blit(overlay, (0, 0))
                g["flash"] -= 1
            elif g["flash"] < 0:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((255, 50, 50, int(80 * abs(g["flash"]) / 8)))
                screen.blit(overlay, (0, 0))
                g["flash"] += 1


                            # HUD
            pygame.draw.rect(screen, DARK, (0, 0, WIDTH, 55))
            pygame.draw.line(screen, ORANGE, (0, 55), (WIDTH, 55), 2)
 
            txt(f"Score: {g['score']}", font_med, WHITE, 90, 28)
            txt(f"Level {g['level']} — {cfg['label']}", font_med, YELLOW, WIDTH // 2, 28)
 
            # Lives hearts
            for i in range(MAX_LIVES):
                col = RED if i < g["lives"] else GRAY
                pygame.draw.circle(screen, col, (WIDTH - 30 - i * 30, 28), 10)
 
            # Progress bar
            prog = g["eggs_caught"] / cfg["eggs_to_next"]
            bar_w = 200
            pygame.draw.rect(screen, GRAY, (WIDTH // 2 - bar_w // 2, 58, bar_w, 8), border_radius=4)
            pygame.draw.rect(screen, GREEN, (WIDTH // 2 - bar_w // 2, 58, int(bar_w * prog), 8), border_radius=4)
 
            txt("ESC to quit", font_tiny, GRAY, WIDTH - 55, HEIGHT - 20)
 
        # ── LEVEL UP ──────────────────────────────────────────────────────────
        elif g["state"] == STATE_LEVEL_UP:
            cfg = LEVEL_SETTINGS[g["level"]]
            txt(f"LEVEL {g['level']}!", font_big, YELLOW, WIDTH // 2, 250)
            txt(cfg["label"], font_med, ORANGE, WIDTH // 2, 320)
            txt(f"Score so far: {g['score']}", font_med, WHITE, WIDTH // 2, 390)
            txt(f"Speed ↑  Catch {cfg['eggs_to_next']} more eggs", font_small, GREEN, WIDTH // 2, 450)
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                txt("Press SPACE to continue", font_med, WHITE, WIDTH // 2, 530)
 
        # ── GAME OVER ─────────────────────────────────────────────────────────
        elif g["state"] == STATE_GAME_OVER:
            txt("GAME OVER", font_big, RED, WIDTH // 2, 240)
            txt(f"Final Score: {g['score']}", font_med, WHITE, WIDTH // 2, 330)
            txt(f"High Score:  {max(high_score, g['score'])}", font_med, GOLD, WIDTH // 2, 390)
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                txt("Press SPACE to play again", font_med, WHITE, WIDTH // 2, 480)
 
        # ── WIN ───────────────────────────────────────────────────────────────
        elif g["state"] == STATE_WIN:
            txt("YOU WIN! 🎉", font_big, GREEN, WIDTH // 2, 220)
            txt("All 5 levels cleared!", font_med, YELLOW, WIDTH // 2, 310)
            txt(f"Final Score: {g['score']}", font_med, WHITE, WIDTH // 2, 380)
            txt(f"High Score:  {max(high_score, g['score'])}", font_med, GOLD, WIDTH // 2, 440)
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                txt("Press SPACE to play again", font_med, WHITE, WIDTH // 2, 530)
 
        pygame.display.flip()
 
    pygame.quit()
    sys.exit()
 
 
if __name__ == "__main__":
    main()