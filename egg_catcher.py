import pygame
import random
import sys
import math

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()

# ── Screen / fullscreen setup ─────────────────────────────────────────────────
INFO        = pygame.display.Info()
NATIVE_W    = INFO.current_w
NATIVE_H    = INFO.current_h
WIN_W, WIN_H = 620, 750          # windowed size
is_fullscreen = False

def make_screen(fullscreen):
    if fullscreen:
        return pygame.display.set_mode((NATIVE_W, NATIVE_H), pygame.FULLSCREEN)
    return pygame.display.set_mode((WIN_W, WIN_H))

screen = make_screen(False)
pygame.display.set_caption("Egg Catcher")

def get_dims():
    return screen.get_width(), screen.get_height()

FPS = 60

# Colours
C_WHITE  = (255, 255, 255)
C_YELLOW = (255, 225,  60)
C_ORANGE = (255, 145,  30)
C_RED    = (230,  65,  65)
C_GREEN  = (60,  210, 120)
C_BLUE   = (90,  160, 255)
C_GRAY   = (120, 120, 150)
C_GOLD   = (255, 205,  20)
C_PURPLE = (175,  85, 235)
C_TEAL   = (40,  210, 190)
C_PINK   = (255, 100, 180)
C_ACCENT = (120,  80, 255)

LEVEL_CFG = {
    1: {"speed": 3,  "spawn": 80, "need": 10, "label": "Easy",   "sky1": (8,10,35),   "sky2": (18,12,50)},
    2: {"speed": 5,  "spawn": 60, "need": 20, "label": "Medium", "sky1": (8,18,40),   "sky2": (5,30,55)},
    3: {"speed": 7,  "spawn": 45, "need": 30, "label": "Hard",   "sky1": (30,8,40),   "sky2": (50,10,60)},
    4: {"speed": 9,  "spawn": 30, "need": 40, "label": "Expert", "sky1": (40,8,8),    "sky2": (60,15,10)},
    5: {"speed": 11, "spawn": 20, "need": 50, "label": "Insane", "sky1": (50,5,5),    "sky2": (80,10,10)},
}
MAX_LEVEL  = 5
MAX_LIVES  = 5
BASKET_W   = 110
BASKET_H   = 32
EGG_RX, EGG_RY = 18, 23
HUD_H      = 70

EGG_COLOURS = [C_YELLOW, C_WHITE, C_GREEN, C_BLUE, C_PURPLE, C_RED, C_ORANGE, C_TEAL, C_PINK]

# ── Gradient cache ─────────────────────────────────────────────────────────────
_grad_cache = {}
def get_gradient(sky1, sky2, w, h):
    key = (sky1, sky2, w, h)
    if key not in _grad_cache:
        surf = pygame.Surface((w, h))
        for y in range(h):
            t = y / h
            r = int(sky1[0] + (sky2[0]-sky1[0])*t)
            g = int(sky1[1] + (sky2[1]-sky1[1])*t)
            b = int(sky1[2] + (sky2[2]-sky1[2])*t)
            pygame.draw.line(surf, (r,g,b), (0,y), (w,y))
        _grad_cache[key] = surf
    return _grad_cache[key]

# ── Drawing helpers ────────────────────────────────────────────────────────────
def rr(surface, color, rect, radius=12, border=0, bc=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and bc:
        pygame.draw.rect(surface, bc, rect, border, border_radius=radius)

def draw_egg(surface, x, y, color, rx=EGG_RX, ry=EGG_RY):
    sh = pygame.Surface((rx*2+4, ry*2+4), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0,0,0,55), (2,4,rx*2,ry*2))
    surface.blit(sh, (x-rx-2, y-ry-2))
    pygame.draw.ellipse(surface, color, (x-rx, y-ry, rx*2, ry*2))
    dc = (max(color[0]-70,0), max(color[1]-70,0), max(color[2]-70,0))
    pygame.draw.ellipse(surface, dc, (x-rx, y-ry, rx*2, ry*2), 2)
    shine = pygame.Surface((10,7), pygame.SRCALPHA)
    pygame.draw.ellipse(shine, (255,255,255,160), (0,0,10,7))
    surface.blit(shine, (x-rx+5, y-ry+5))

def draw_basket(surface, x, y):
    bx = x - BASKET_W//2
    sh = pygame.Surface((BASKET_W+20,14), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0,0,0,45), (0,0,BASKET_W+20,14))
    surface.blit(sh, (bx-10, y+BASKET_H+2))
    pts = [(bx,y),(bx+BASKET_W,y),(bx+BASKET_W-12,y+BASKET_H),(bx+12,y+BASKET_H)]
    pygame.draw.polygon(surface, (180,100,20), pts)
    for i in range(1,3):
        fy = y + i*(BASKET_H//3); sk = i*4
        pygame.draw.line(surface,(140,75,10),(bx+sk,fy),(bx+BASKET_W-sk,fy),2)
    for i in range(1,5):
        lx = bx + i*(BASKET_W//5)
        pygame.draw.line(surface,(140,75,10),(lx,y),(lx-8,y+BASKET_H),2)
    hi = pygame.Surface((BASKET_W,BASKET_H), pygame.SRCALPHA)
    pygame.draw.polygon(hi,(255,200,80,30),[(4,2),(BASKET_W-4,2),(BASKET_W-16,BASKET_H-4),(16,BASKET_H-4)])
    surface.blit(hi,(bx,y))
    rr(surface, C_YELLOW, (bx-6,y-8,BASKET_W+12,14), radius=7)
    rr(surface, C_GOLD,   (bx-6,y-8,BASKET_W+12,14), radius=7, border=2, bc=C_GOLD)
    rs = pygame.Surface((BASKET_W+12,5), pygame.SRCALPHA)
    pygame.draw.rect(rs,(255,255,255,55),(0,0,BASKET_W+12,5),border_radius=5)
    surface.blit(rs,(bx-6,y-8))

def draw_star(surface, cx, cy, r, color):
    pts=[]
    for i in range(10):
        a=math.radians(i*36-90); rad=r if i%2==0 else r//2
        pts.append((cx+rad*math.cos(a), cy+rad*math.sin(a)))
    pygame.draw.polygon(surface, color, pts)

def draw_stars_bg(surface, tick, W, H):
    rng = random.Random(42)
    for _ in range(70):
        sx=rng.randint(0,W); sy=rng.randint(HUD_H+10,H-80)
        phase=rng.random()*math.pi*2
        alpha=int(70+70*math.sin(tick*0.03+phase))
        r=rng.randint(1,2)
        ss=pygame.Surface((r*2+2,r*2+2),pygame.SRCALPHA)
        pygame.draw.circle(ss,(200,200,255,alpha),(r+1,r+1),r)
        surface.blit(ss,(sx-r,sy-r))

def draw_hud(surface, fonts, g, cfg, high_score, tick, W):
    font_med, font_small, font_tiny = fonts
    panel=pygame.Surface((W,HUD_H),pygame.SRCALPHA)
    panel.fill((12,12,40,225))
    surface.blit(panel,(0,0))
    gl=pygame.Surface((W,3),pygame.SRCALPHA)
    for x in range(W):
        a=int(180+60*math.sin(tick*0.04+x*0.02))
        gl.set_at((x,0),(*C_ACCENT,min(255,a)))
        gl.set_at((x,1),(*C_ACCENT,min(110,a//2)))
    surface.blit(gl,(0,HUD_H))
    # Score
    rr(surface,(28,28,68),(10,8,110,54),radius=10)
    surface.blit(font_tiny.render("SCORE",True,C_GRAY), font_tiny.render("SCORE",True,C_GRAY).get_rect(centerx=65,top=12))
    surface.blit(font_med.render(f"{g['score']}",True,C_WHITE), font_med.render(f"{g['score']}",True,C_WHITE).get_rect(centerx=65,top=28))
    # Level
    lcs=[C_GREEN,C_BLUE,C_YELLOW,C_ORANGE,C_RED]
    lc=lcs[g["level"]-1]
    rr(surface,(28,28,68),(W//2-70,6,140,58),radius=10)
    surface.blit(font_tiny.render("LEVEL",True,C_GRAY), font_tiny.render("LEVEL",True,C_GRAY).get_rect(centerx=W//2,top=10))
    surface.blit(font_med.render(f"{g['level']}  {cfg['label']}",True,lc), font_med.render(f"{g['level']}  {cfg['label']}",True,lc).get_rect(centerx=W//2,top=28))
    # Best
    rr(surface,(28,28,68),(W-120,8,110,54),radius=10)
    surface.blit(font_tiny.render("BEST",True,C_GRAY), font_tiny.render("BEST",True,C_GRAY).get_rect(centerx=W-65,top=12))
    surface.blit(font_med.render(f"{max(high_score,g['score'])}",True,C_GOLD), font_med.render(f"{max(high_score,g['score'])}",True,C_GOLD).get_rect(centerx=W-65,top=28))
    # Hearts
    hy=HUD_H+15
    for i in range(MAX_LIVES):
        col=C_RED if i<g["lives"] else (50,30,50)
        hx=W-30-i*28
        pygame.draw.circle(surface,col,(hx-5,hy),7)
        pygame.draw.circle(surface,col,(hx+5,hy),7)
        pygame.draw.polygon(surface,col,[(hx-11,hy+4),(hx+11,hy+4),(hx,hy+16)])
    # Progress bar
    prog=min(1.0,g["eggs_caught"]/cfg["need"])
    bx2=12; by2=HUD_H+13; bw=W-30-MAX_LIVES*28-bx2-10; bh=10
    rr(surface,(40,40,80),(bx2,by2,bw,bh),radius=5)
    if prog>0:
        fc=C_GREEN if prog<0.7 else C_YELLOW if prog<0.9 else C_ORANGE
        rr(surface,fc,(bx2,by2,int(bw*prog),bh),radius=5)
        sh2=pygame.Surface((int(bw*prog),bh//2),pygame.SRCALPHA)
        sh2.fill((255,255,255,40)); surface.blit(sh2,(bx2,by2))
    surface.blit(font_tiny.render(f"{int(prog*100)}%",True,C_GRAY),(bx2+bw+4,by2-1))

# ── Overlay card ──────────────────────────────────────────────────────────────
def draw_card(surface, cx, cy, w, h, fonts, title, lines, blink_text, tick):
    font_big, font_med, font_small = fonts
    cs=pygame.Surface((w,h),pygame.SRCALPHA)
    cs.fill((14,10,48,215))
    pygame.draw.rect(cs,(100,80,220,90),(0,0,w,h),2,border_radius=18)
    surface.blit(cs,(cx-w//2,cy-h//2))
    gb=pygame.Surface((w,4),pygame.SRCALPHA)
    for x in range(w):
        a=int(180+60*math.sin(tick*0.05+x*0.04))
        gb.set_at((x,0),(*C_ACCENT,min(255,a)))
    surface.blit(gb,(cx-w//2,cy-h//2))
    sh=font_big.render(title,True,C_ACCENT)
    ts=font_big.render(title,True,C_WHITE)
    surface.blit(sh,sh.get_rect(center=(cx+3,cy-h//2+52)))
    surface.blit(ts,ts.get_rect(center=(cx,cy-h//2+50)))
    sep=cy-h//2+80
    pygame.draw.line(surface,C_ACCENT,(cx-w//2+30,sep),(cx+w//2-30,sep),1)
    for i,(text,col) in enumerate(lines):
        s=font_med.render(text,True,col)
        surface.blit(s,s.get_rect(center=(cx,sep+32+i*40)))
    if (tick//28)%2==0:
        cta=font_small.render(blink_text,True,C_WHITE)
        cr=cta.get_rect(center=(cx,cy+h//2-38))
        rr(surface,C_ACCENT,cr.inflate(24,12),radius=8)
        surface.blit(cta,cr)

# ── HOME SCREEN ───────────────────────────────────────────────────────────────
class MenuEgg:
    """An egg that loops from top to bottom on the menu screen."""
    def __init__(self, W, H):
        self.W=W; self.H=H
        self.reset()

    def reset(self):
        self.x = random.randint(30, self.W-30)
        self.y = random.randint(-self.H, -40)
        self.speed = random.uniform(1.2, 3.5)
        self.color = random.choice(EGG_COLOURS)
        self.golden = random.random() < 0.12
        if self.golden: self.color = C_GOLD
        self.wobble = random.uniform(0, math.pi*2)
        self.rx = random.randint(14, 22)
        self.ry = random.randint(18, 28)
        self.spin = random.uniform(-0.04, 0.04)
        self.angle = 0
        self.alpha = random.randint(120, 230)

    def update(self, tick):
        self.x += math.sin(tick*0.03+self.wobble)*0.6
        self.x = max(self.rx+5, min(self.W-self.rx-5, self.x))
        self.y += self.speed
        self.angle += self.spin
        if self.y - self.ry > self.H:
            self.reset()
            self.y = -self.ry

    def draw(self, surface):
        s = pygame.Surface((self.rx*2+8, self.ry*2+8), pygame.SRCALPHA)
        # shadow
        pygame.draw.ellipse(s,(0,0,0,40),(4,6,self.rx*2,self.ry*2))
        # body
        pygame.draw.ellipse(s,(*self.color,self.alpha),(2,2,self.rx*2,self.ry*2))
        dc=(max(self.color[0]-70,0),max(self.color[1]-70,0),max(self.color[2]-70,0),self.alpha)
        pygame.draw.ellipse(s,dc,(2,2,self.rx*2,self.ry*2),2)
        # shine
        pygame.draw.ellipse(s,(255,255,255,110),(7,6,9,6))
        surface.blit(s,(int(self.x)-self.rx-4, int(self.y)-self.ry-4))
        if self.golden:
            draw_star(surface,int(self.x),int(self.y)-self.ry-10,6,C_GOLD)

class MenuBasket:
    def __init__(self, W, H):
        self.W=W; self.H=H
        self.x = W//2
        self.target_x = W//2
        self.caught = []   # (x,y,color,life)
        self.timer = 0

    def update(self, tick, eggs):
        # auto-aim at nearest egg
        nearest = None; best=9999
        for e in eggs:
            if e.y > self.H*0.3:
                d=abs(e.x-self.x)
                if d<best: best=d; nearest=e
        if nearest:
            self.target_x = nearest.x
        else:
            self.target_x = self.W//2 + int(100*math.sin(tick*0.018))
        self.x += (self.target_x - self.x)*0.08
        self.x = max(BASKET_W//2+5, min(self.W-BASKET_W//2-5, self.x))
        BY = self.H - 120
        # check catches for demo
        for e in eggs[:]:
            if abs(e.x-self.x)<BASKET_W//2+EGG_RX-6 and abs(e.y-BY)<EGG_RY+12:
                self.caught.append([e.x, BY, e.color, 40])
                e.reset(); e.y=-EGG_RY
        self.caught=[c for c in self.caught if c[3]>0]
        for c in self.caught: c[1]-=1.5; c[3]-=1

    def draw(self, surface):
        BY = self.H - 120
        draw_basket(surface, int(self.x), BY)
        for (cx,cy,col,life) in self.caught:
            a=min(255,int(255*life/40))
            ts=pygame.Surface((EGG_RX*2,EGG_RY*2),pygame.SRCALPHA)
            pygame.draw.ellipse(ts,(*col,a),(0,0,EGG_RX*2,EGG_RY*2))
            surface.blit(ts,(int(cx)-EGG_RX,int(cy)-EGG_RY))

class NeonRing:
    """Animated neon ring that pulses behind the title."""
    def __init__(self, cx, cy):
        self.cx=cx; self.cy=cy
        self.base_r=140
        self.phase=0

    def draw(self, surface, tick):
        for i in range(3):
            r=self.base_r+i*18+int(8*math.sin(tick*0.04+i*1.2))
            alpha=int(60-i*15+30*math.sin(tick*0.05+i))
            ring=pygame.Surface((r*2+4,r*2+4),pygame.SRCALPHA)
            col=(*C_ACCENT,max(0,alpha))
            pygame.draw.circle(ring,col,(r+2,r+2),r,2+i)
            surface.blit(ring,(self.cx-r-2,self.cy-r-2))

class ShootingStar:
    def __init__(self, W):
        self.W=W
        self.reset()

    def reset(self):
        self.x=random.randint(0,self.W)
        self.y=random.randint(0,200)
        self.vx=random.uniform(4,10)*random.choice([-1,1])
        self.vy=random.uniform(2,5)
        self.life=random.randint(30,60)
        self.max_life=self.life
        self.len=random.randint(30,80)

    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.life-=1

    def draw(self, surface):
        a=int(200*self.life/self.max_life)
        end=(self.x-self.vx*(self.len/6),self.y-self.vy*(self.len/6))
        ss=pygame.Surface((abs(int(self.vx*self.len/6))+4,abs(int(self.vy*self.len/6))+4),pygame.SRCALPHA)
        # just draw on main surface directly
        pygame.draw.line(surface,(255,255,255,a),(int(self.x),int(self.y)),(int(end[0]),int(end[1])),2)

    def done(self): return self.life<=0

def draw_menu(surface, tick, menu_eggs, menu_basket, neon_ring, shooting_stars, fonts, high_score, W, H):
    font_big, font_med, font_small, font_tiny = fonts

    # Background — deep purple-blue nebula
    surface.blit(get_gradient((5,5,25),(20,8,45),W,H),(0,0))

    # Nebula glow blobs
    for i,(nx,ny,nr,nc) in enumerate([
        (W*0.2, H*0.3, 120, (40,20,80)),
        (W*0.8, H*0.2, 100, (20,40,90)),
        (W*0.5, H*0.7, 150, (60,20,60)),
        (W*0.1, H*0.8, 90,  (20,60,80)),
        (W*0.9, H*0.6, 110, (80,30,40)),
    ]):
        pulse=int(20*math.sin(tick*0.02+i*1.3))
        nb=pygame.Surface((nr*2+pulse,nr*2+pulse),pygame.SRCALPHA)
        pygame.draw.circle(nb,(*nc,22),(nr+pulse//2,nr+pulse//2),nr+pulse//2)
        surface.blit(nb,(int(nx)-nr,int(ny)-nr))

    # Stars twinkling
    draw_stars_bg(surface, tick, W, H)

    # Shooting stars
    for ss in shooting_stars:
        ss.draw(surface)

    # Falling eggs behind card
    for e in menu_eggs:
        e.draw(surface)

    # Neon rings behind title
    neon_ring.draw(surface, tick)

    # ── Title card ────────────────────────────────────────────────────────────
    card_w = min(500, W-40)
    card_h = 360
    card_cx = W//2
    card_cy = H//2 - 60

    # Card glass panel
    cs=pygame.Surface((card_w,card_h),pygame.SRCALPHA)
    cs.fill((10,8,40,200))
    pygame.draw.rect(cs,(120,80,255,70),(0,0,card_w,card_h),2,border_radius=22)
    surface.blit(cs,(card_cx-card_w//2,card_cy-card_h//2))

    # Animated rainbow top border
    bw=card_w; bh=4; bsurf=pygame.Surface((bw,bh),pygame.SRCALPHA)
    for x in range(bw):
        hue=(x/bw*360+tick*1.2)%360
        hue_r=abs(hue-180)/180
        r2=int(255*max(0,1-abs(hue-0)/60) + 255*max(0,1-abs(hue-360)/60))
        g2=int(255*max(0,1-abs(hue-120)/60))
        b2=int(255*max(0,1-abs(hue-240)/60))
        bsurf.set_at((x,0),(min(255,r2),min(255,g2),min(255,b2),220))
        bsurf.set_at((x,1),(min(255,r2),min(255,g2),min(255,b2),110))
    surface.blit(bsurf,(card_cx-card_w//2,card_cy-card_h//2))

    # Title with colour wave
    title="EGG CATCHER"
    title_y=card_cy-card_h//2+62
    total_w=sum(font_big.size(c)[0] for c in title)
    sx=card_cx-total_w//2
    for ci,ch in enumerate(title):
        wave=int(6*math.sin(tick*0.06+ci*0.4))
        hue=(ci/len(title)*360+tick*2)%360
        # simple hue to rgb
        h6=hue/60; fi=int(h6); f=h6-fi
        p=0; q=int(255*(1-f)); tv=int(255*f)
        rgb_map=[(255,tv,p),(q,255,p),(p,255,tv),(p,q,255),(tv,p,255),(255,p,q)]
        tc=rgb_map[fi%6]
        # shadow
        sh_s=font_big.render(ch,True,(0,0,0))
        surface.blit(sh_s,(sx+3,title_y+wave+3))
        cs2=font_big.render(ch,True,tc)
        surface.blit(cs2,(sx,title_y+wave))
        sx+=font_big.size(ch)[0]

    # Separator with glow
    sep_y=card_cy-card_h//2+108
    sep_surf=pygame.Surface((card_w-60,3),pygame.SRCALPHA)
    for x in range(card_w-60):
        a=int(150+80*math.sin(tick*0.05+x*0.03))
        sep_surf.set_at((x,0),(*C_ACCENT,min(255,a)))
        sep_surf.set_at((x,1),(*C_ACCENT,min(80,a//2)))
    surface.blit(sep_surf,(card_cx-card_w//2+30,sep_y))

    # Info rows with icons
    rows=[
        ("🎮  Arrow Keys to move basket",   C_GRAY),
        ("⭐  Golden eggs = 5 pts bonus!",   C_GOLD),
        ("🔥  Catch combos for bonus pts",   C_ORANGE),
        (f"🏆  Best Score:  {high_score}",   C_GREEN),
        ("F11  Toggle Fullscreen",           (80,80,120)),
    ]
    for i,(txt,col) in enumerate(rows):
        s=font_small.render(txt,True,col)
        surface.blit(s,s.get_rect(centerx=card_cx,top=sep_y+18+i*38))

    # Pulsing START button
    btn_y=card_cy+card_h//2-44
    btn_w=260; btn_h=46
    pulse2=int(4*math.sin(tick*0.08))
    # glow around button
    for gi in range(3,0,-1):
        ga=pygame.Surface((btn_w+gi*8,btn_h+gi*8),pygame.SRCALPHA)
        pygame.draw.rect(ga,(*C_ACCENT,20+gi*10),(0,0,btn_w+gi*8,btn_h+gi*8),border_radius=24)
        surface.blit(ga,(card_cx-(btn_w+gi*8)//2,btn_y-(gi*4)//2+pulse2))
    rr(surface,C_ACCENT,(card_cx-btn_w//2,btn_y+pulse2,btn_w,btn_h),radius=23)
    # shine on button
    sh3=pygame.Surface((btn_w,btn_h//2),pygame.SRCALPHA)
    sh3.fill((255,255,255,30))
    surface.blit(sh3,(card_cx-btn_w//2,btn_y+pulse2))
    btn_txt=font_med.render("▶  PRESS SPACE",True,C_WHITE)
    surface.blit(btn_txt,btn_txt.get_rect(center=(card_cx,btn_y+btn_h//2+pulse2)))

    # Demo basket (auto-plays)
    menu_basket.draw(surface)

    # Small egg decorations near card edges
    for i in range(3):
        ex2=card_cx-card_w//2-30
        ey2=card_cy-card_h//2+60+i*100+int(6*math.sin(tick*0.04+i))
        draw_egg(surface,ex2,ey2,EGG_COLOURS[i],12,15)
        ex3=card_cx+card_w//2+30
        ey3=card_cy-card_h//2+80+i*90+int(6*math.sin(tick*0.04+i+2))
        draw_egg(surface,ex3,ey3,EGG_COLOURS[i+3],12,15)

# ── Game classes ───────────────────────────────────────────────────────────────
class Egg:
    def __init__(self, speed, W, H):
        self.W=W; self.H=H
        self.x=random.randint(EGG_RX+15, W-EGG_RX-15)
        self.y=-EGG_RY
        self.speed=speed+random.uniform(-0.8,0.8)
        self.color=random.choice(EGG_COLOURS)
        self.golden=random.random()<0.08
        self.wobble=random.uniform(0,math.pi*2)
        if self.golden: self.color=C_GOLD
        self.trail=[]

    def update(self, tick):
        self.x+=math.sin(tick*0.05+self.wobble)*0.4
        self.x=max(EGG_RX+5, min(self.W-EGG_RX-5, self.x))
        self.trail.append((int(self.x),int(self.y)))
        if len(self.trail)>6: self.trail.pop(0)
        self.y+=self.speed

    def draw(self, surface):
        for i,(tx,ty) in enumerate(self.trail):
            a=int(35*(i/max(1,len(self.trail))))
            ts=pygame.Surface((EGG_RX*2,EGG_RY*2),pygame.SRCALPHA)
            pygame.draw.ellipse(ts,(max(self.color[0]-40,0),max(self.color[1]-40,0),max(self.color[2]-40,0),a),(0,0,EGG_RX*2,EGG_RY*2))
            surface.blit(ts,(tx-EGG_RX,ty-EGG_RY))
        draw_egg(surface,int(self.x),int(self.y),self.color)
        if self.golden: draw_star(surface,int(self.x),int(self.y)-EGG_RY-10,7,C_GOLD)

    def caught(self, bx, BY):
        return (abs(self.x-bx)<BASKET_W//2+EGG_RX-6 and abs(self.y-BY)<EGG_RY+12)

    def missed(self, H):
        return self.y-EGG_RY>H

class Particle:
    def __init__(self, x, y, color, mode="catch"):
        self.x=x; self.y=y; self.color=color
        if mode=="catch":
            a=random.uniform(0,math.pi*2); sp=random.uniform(2,6)
            self.vx=math.cos(a)*sp; self.vy=math.sin(a)*sp-3
            self.life=random.randint(25,40); self.size=random.randint(3,6)
            self.shape=random.choice(["circle","star"])
        else:
            self.vx=random.uniform(-2,2); self.vy=random.uniform(-4,-1)
            self.life=random.randint(15,25); self.size=random.randint(2,4)
            self.shape="circle"

    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=0.25; self.vx*=0.97; self.life-=1

    def draw(self, surface):
        if self.life<=0: return
        al=max(0,int(255*self.life/40))
        r,g2,b=(max(0,min(255,int(self.color[0]))),max(0,min(255,int(self.color[1]))),max(0,min(255,int(self.color[2]))))
        ps=pygame.Surface((self.size*2+2,self.size*2+2),pygame.SRCALPHA)
        if self.shape=="star" and self.size>3:
            draw_star(ps,self.size+1,self.size+1,self.size,(r,g2,b))
        else:
            pygame.draw.circle(ps,(r,g2,b,al),(self.size+1,self.size+1),self.size)
        surface.blit(ps,(int(self.x)-self.size,int(self.y)-self.size))

class ScorePopup:
    def __init__(self, x, y, text, color, font):
        self.x=x; self.y=y; self.text=text; self.color=color; self.font=font
        self.life=45; self.max_life=45

    def update(self): self.y-=1.2; self.life-=1

    def draw(self, surface):
        al=max(0,int(255*self.life/self.max_life))
        s=self.font.render(self.text,True,self.color); s.set_alpha(al)
        surface.blit(s,s.get_rect(center=(int(self.x),int(self.y))))

# ── States ─────────────────────────────────────────────────────────────────────
S_MENU="menu"; S_PLAY="play"; S_LVL="lvlup"; S_OVER="over"; S_WIN="win"

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    global screen, is_fullscreen

    clock=pygame.time.Clock()
    tick=0

    def load_fonts():
        try:
            return (pygame.font.SysFont("Segoe UI",56,bold=True),
                    pygame.font.SysFont("Segoe UI",30,bold=True),
                    pygame.font.SysFont("Segoe UI",22),
                    pygame.font.SysFont("Segoe UI",16,bold=True),
                    pygame.font.SysFont("Segoe UI",26,bold=True))
        except:
            return (pygame.font.SysFont("Arial",56,bold=True),
                    pygame.font.SysFont("Arial",30,bold=True),
                    pygame.font.SysFont("Arial",22),
                    pygame.font.SysFont("Arial",16,bold=True),
                    pygame.font.SysFont("Arial",26,bold=True))

    font_big,font_med,font_small,font_tiny,font_popup=load_fonts()

    W,H=get_dims()

    # Menu animation objects
    menu_eggs=[MenuEgg(W,H) for _ in range(22)]
    menu_basket=MenuBasket(W,H)
    neon_ring=NeonRing(W//2, H//2-60)
    shooting_stars=[ShootingStar(W) for _ in range(3)]
    ss_timer=0

    def reset_game():
        W2,H2=get_dims()
        return {
            "state": S_MENU,
            "score": 0,
            "lives": MAX_LIVES,
            "level": 1,
            "eggs_caught": 0,
            "basket_x": W2//2,
            "eggs": [],
            "particles": [],
            "popups": [],
            "spawn_timer": 0,
            "flash": 0,
            "combo": 0,
        }

    g=reset_game()
    high_score=0

    running=True
    while running:
        clock.tick(FPS)
        tick+=1
        W,H=get_dims()
        BASKET_Y=H-85
        ss_timer+=1

        cfg=LEVEL_CFG[g["level"]]

        # Background
        screen.blit(get_gradient(cfg["sky1"],cfg["sky2"],W,H),(0,0))
        draw_stars_bg(screen,tick,W,H)

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    if is_fullscreen:
                        is_fullscreen=False
                        screen=make_screen(False)
                        W,H=get_dims()
                        menu_eggs=[MenuEgg(W,H) for _ in range(22)]
                        menu_basket=MenuBasket(W,H)
                        neon_ring=NeonRing(W//2,H//2-60)
                    else:
                        running=False
                if event.key==pygame.K_F11:
                    is_fullscreen=not is_fullscreen
                    screen=make_screen(is_fullscreen)
                    W,H=get_dims()
                    menu_eggs=[MenuEgg(W,H) for _ in range(22)]
                    menu_basket=MenuBasket(W,H)
                    neon_ring=NeonRing(W//2,H//2-60)
                    _grad_cache.clear()
                if g["state"]==S_MENU:
                    if event.key in (pygame.K_RETURN,pygame.K_SPACE):
                        g=reset_game(); g["state"]=S_PLAY
                elif g["state"] in (S_OVER,S_WIN):
                    if event.key in (pygame.K_RETURN,pygame.K_SPACE):
                        high_score=max(high_score,g["score"])
                        g=reset_game(); g["state"]=S_MENU
                elif g["state"]==S_LVL:
                    if event.key in (pygame.K_RETURN,pygame.K_SPACE):
                        g["state"]=S_PLAY

        # ── MENU ──────────────────────────────────────────────────────────────
        if g["state"]==S_MENU:
            # Update menu anims
            for e in menu_eggs: e.update(tick)
            menu_basket.update(tick,menu_eggs)
            for ss in shooting_stars: ss.update()
            shooting_stars=[ss for ss in shooting_stars if not ss.done()]
            if ss_timer%120==0: shooting_stars.append(ShootingStar(W))

            draw_menu(screen, tick, menu_eggs, menu_basket, neon_ring,
                      shooting_stars, (font_big,font_med,font_small,font_tiny),
                      high_score, W, H)

            # F11 hint bottom
            hint=font_tiny.render("F11 — Toggle Fullscreen   |   ESC — Quit",True,(55,55,85))
            screen.blit(hint,hint.get_rect(centerx=W//2,bottom=H-8))

        # ── PLAYING ───────────────────────────────────────────────────────────
        elif g["state"]==S_PLAY:
            pygame.draw.line(screen,(60,40,100),(0,H-55),(W,H-55),1)
            keys=pygame.key.get_pressed()
            spd=8
            if keys[pygame.K_LEFT]:  g["basket_x"]=max(BASKET_W//2+5,g["basket_x"]-spd)
            if keys[pygame.K_RIGHT]: g["basket_x"]=min(W-BASKET_W//2-5,g["basket_x"]+spd)

            g["spawn_timer"]+=1
            if g["spawn_timer"]>=cfg["spawn"]:
                g["spawn_timer"]=0; g["eggs"].append(Egg(cfg["speed"],W,H))

            caught,missed=[],[]
            for egg in g["eggs"]:
                egg.update(tick)
                if egg.caught(g["basket_x"],BASKET_Y): caught.append(egg)
                elif egg.missed(H): missed.append(egg)

            for egg in caught:
                g["eggs"].remove(egg)
                g["combo"]+=1
                pts=5 if egg.golden else 1
                if g["combo"]>=3: pts+=1
                g["score"]+=pts; g["eggs_caught"]+=1; g["flash"]=10
                lbl=f"+{pts}"+(" COMBO!" if g["combo"]>=3 else "")
                g["popups"].append(ScorePopup(egg.x,BASKET_Y-20,lbl,C_GOLD if egg.golden else C_GREEN,font_popup))
                for _ in range(16): g["particles"].append(Particle(egg.x,BASKET_Y,egg.color,"catch"))

            for egg in missed:
                g["eggs"].remove(egg)
                g["lives"]-=1; g["combo"]=0; g["flash"]=-10
                g["popups"].append(ScorePopup(egg.x,H-70,"MISS!",C_RED,font_popup))
                for _ in range(10): g["particles"].append(Particle(egg.x,H-60,C_RED,"miss"))

            g["particles"]=[p for p in g["particles"] if p.life>0]
            for p in g["particles"]: p.update(); p.draw(screen)

            g["popups"]=[p for p in g["popups"] if p.life>0]
            for p in g["popups"]: p.update(); p.draw(screen)

            if g["eggs_caught"]>=cfg["need"]:
                g["eggs_caught"]=0; g["eggs"]=[]; g["combo"]=0
                g["state"]=S_WIN if g["level"]>=MAX_LEVEL else S_LVL
                if g["state"]==S_LVL: g["level"]+=1

            if g["lives"]<=0: g["state"]=S_OVER

            for egg in g["eggs"]: egg.draw(screen)
            draw_basket(screen,g["basket_x"],BASKET_Y)

            if g["flash"]!=0:
                ov=pygame.Surface((W,H),pygame.SRCALPHA)
                if g["flash"]>0:
                    ov.fill((255,255,100,int(70*g["flash"]/10))); g["flash"]-=1
                else:
                    ov.fill((255,50,50,int(70*abs(g["flash"])/10))); g["flash"]+=1
                screen.blit(ov,(0,0))

            if g["combo"]>=3:
                cs=font_med.render(f"x{g['combo']} COMBO!",True,C_ORANGE)
                pulse=int(4*math.sin(tick*0.2))
                screen.blit(cs,cs.get_rect(centerx=W//2,top=HUD_H+95+pulse))

            draw_hud(screen,(font_med,font_small,font_tiny),g,cfg,high_score,tick,W)
            screen.blit(font_tiny.render("F11 Fullscreen  |  ESC Quit",True,(55,55,80)),(8,H-20))

        # ── LEVEL UP ──────────────────────────────────────────────────────────
        elif g["state"]==S_LVL:
            lcs=[C_GREEN,C_BLUE,C_YELLOW,C_ORANGE,C_RED]
            lc=lcs[g["level"]-1]
            draw_card(screen,W//2,H//2,min(420,W-40),300,
                      (font_big,font_med,font_small),
                      f"LEVEL  {g['level']}",
                      [(cfg["label"],lc),(f"Score: {g['score']}",C_WHITE),(f"Catch {cfg['need']} eggs",C_GRAY)],
                      "PRESS  SPACE  TO  CONTINUE",tick)

        # ── GAME OVER ─────────────────────────────────────────────────────────
        elif g["state"]==S_OVER:
            draw_card(screen,W//2,H//2,min(420,W-40),300,
                      (font_big,font_med,font_small),
                      "GAME  OVER",
                      [(f"Score: {g['score']}",C_WHITE),(f"Best:  {max(high_score,g['score'])}",C_GOLD),(f"Level reached: {g['level']}",C_GRAY)],
                      "PRESS  SPACE  TO  RETRY",tick)

        # ── WIN ───────────────────────────────────────────────────────────────
        elif g["state"]==S_WIN:
            rng2=random.Random(tick//3)
            for _ in range(22):
                cx2=rng2.randint(0,W); cy2=rng2.randint(0,H)
                col=rng2.choice(EGG_COLOURS)
                pygame.draw.circle(screen,col,(cx2,cy2),rng2.randint(3,8))
            draw_card(screen,W//2,H//2,min(440,W-40),310,
                      (font_big,font_med,font_small),
                      "YOU  WIN!",
                      [("All 5 Levels Cleared!",C_YELLOW),(f"Final Score: {g['score']}",C_WHITE),(f"Best Score: {max(high_score,g['score'])}",C_GOLD)],
                      "PRESS  SPACE  TO  PLAY  AGAIN",tick)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__=="__main__":
    main()