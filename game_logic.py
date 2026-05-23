rom pygame import *
from random import randint, choice

# ---------------- INIT ----------------
init()
mixer.init()

WIDTH, HEIGHT = 1000, 600
FPS = 60

window = display.set_mode((WIDTH, HEIGHT))
display.set_caption("Ping Pong")

clock = time.Clock()

# ---------------- COLORS ----------------
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (20, 30, 70)
DARK = (8, 12, 30)

# ---------------- PARTICLES ----------------
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = randint(-6, 6)
        self.vy = randint(-6, 6)
        self.life = 35
        self.size = randint(2, 5)
        self.color = (0, randint(150, 255), 255)

    def update(self):
        self.x += self.vx
        self.y += self.vy

        self.vx *= 0.95
        self.vy *= 0.95

        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            draw.circle(
                surface,
                self.color,
                (int(self.x), int(self.y)),
                self.size
            )

# ---------------- STARS ----------------
class Star:
    def __init__(self):
        self.x = randint(0, WIDTH)
        self.y = randint(0, HEIGHT)
        self.speed = randint(1, 3)
        self.size = randint(1, 3)

    def update(self):
        self.y += self.speed

        if self.y > HEIGHT:
            self.y = 0
            self.x = randint(0, WIDTH)

    def draw(self, surface):
        draw.circle(
            surface,
            (200, 220, 255),
            (self.x, self.y),
            self.size
        )
