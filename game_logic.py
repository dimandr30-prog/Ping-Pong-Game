from pygame import *
from random import randint, choice

# ---------------- INIT ----------------
init()
mixer.init()

# ---------------- MUSIC ----------------
mixer.music.load("background_music.ogg")
mixer.music.set_volume(0.6)
mixer.music.play(-1)

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
            draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

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
        draw.circle(surface, (200, 220, 255), (self.x, self.y), self.size)

stars = [Star() for _ in range(100)]
particles = []
menu_particles = []

def spawn_explosion(x, y):
    for _ in range(20):
        particles.append(Particle(x, y))

# ---------------- SPRITES ----------------
class GameSprite(sprite.Sprite):
    def __init__(self, color, x, y, w, h, speed):
        super().__init__()
        self.image = Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# ---------------- PLAYER ----------------
class Player(GameSprite):
    def __init__(self, x, y, controls):
        super().__init__(WHITE, x, y, 18, 120, 7)
        self.up = controls[0]
        self.down = controls[1]

    def update(self):
        keys = key.get_pressed()
        if keys[self.up]:
            self.rect.y -= self.speed
        if keys[self.down]:
            self.rect.y += self.speed
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

# ---------------- BOT ----------------
class Bot(GameSprite):
    def __init__(self, x, y, difficulty):
        super().__init__(WHITE, x, y, 18, 120, 5)
        self.difficulty = difficulty

    def update(self, ball):
        if self.difficulty == "easy":
            speed = 4
        elif self.difficulty == "hard":
            speed = 9
        elif self.difficulty == "infinite":
            speed = 12
        else:
            speed = 6

        if self.rect.centery < ball.rect.centery:
            self.rect.y += speed
        if self.rect.centery > ball.rect.centery:
            self.rect.y -= speed

        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

# ---------------- BALL ----------------
class Ball(GameSprite):
    def __init__(self):
        super().__init__(CYAN, WIDTH // 2, HEIGHT // 2, 20, 20, 5)
        self.reset()

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed_x = choice([-5, 5])
        self.speed_y = choice([-5, 5])
        self.base_speed = 5

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1

    def collide(self, paddle):
        if self.rect.colliderect(paddle.rect):
            spawn_explosion(self.rect.centerx, self.rect.centery)
            self.speed_x *= -1

            if self.speed_x > 0:
                self.speed_x += 0.5
            else:
                self.speed_x -= 0.5

# ---------------- MUSIC FIX ----------------
def update_music_volume():
    if state == "menu":
        mixer.music.set_volume(0.6)
    elif state == "game":
        mixer.music.set_volume(1.0)
    else:
        mixer.music.set_volume(0.7)

# ---------------- FONTS ----------------
font_big = font.SysFont("Arial", 60)
font_small = font.SysFont("Arial", 28)

# ---------------- SETTINGS ----------------
settings = {
    "easy": {"limit": 12, "bot": True},
    "normal": {"limit": 12, "bot": True},
    "hard": {"limit": 12, "bot": True},
    "infinite": {"limit": 999999, "bot": True},
    "2 players": {"limit": 12, "bot": False}
}
