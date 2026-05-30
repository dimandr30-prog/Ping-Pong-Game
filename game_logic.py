from pygame import *
from random import randint, choice

init()
mixer.init()

mixer.music.load("background_music.ogg")
mixer.music.set_volume(0.6)
mixer.music.play(-1)

hit_sound = mixer.Sound("hit_impact.ogg")

WIDTH, HEIGHT = 1000, 600
FPS = 60

window = display.set_mode((WIDTH, HEIGHT))
display.set_caption("Ping Pong")

clock = time.Clock()

WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (20, 30, 70)
DARK = (8, 12, 30)

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

class GameSprite(sprite.Sprite):
    def __init__(self, color, x, y, w, h, speed):
        super().__init__()
        self.image = Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

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
            hit_sound.play()

            self.speed_x *= -1

            if self.speed_x > 0:
                self.speed_x += 0.5
            else:
                self.speed_x -= 0.5

def update_music_volume():
    if state == "menu":
        mixer.music.set_volume(0.6)
    elif state == "game":
        mixer.music.set_volume(1.0)
    else:
        mixer.music.set_volume(0.7)

font_big = font.SysFont("Arial", 60)
font_small = font.SysFont("Arial", 28)

settings = {
    "easy": {"limit": 12, "bot": True},
    "normal": {"limit": 12, "bot": True},
    "hard": {"limit": 12, "bot": True},
    "infinite": {"limit": 999999, "bot": True},
    "2 players": {"limit": 12, "bot": False}
}

state = "menu"
difficulty = "easy"

player1 = None
player2 = None
ball = None

score1 = 0
score2 = 0
paused = False

def start_game(mode):
    global player1, player2, ball, score1, score2

    particles.clear()
    menu_particles.clear()

    player1 = Player(40, HEIGHT // 2 - 60, (K_w, K_s))

    if settings[mode]["bot"]:
        player2 = Bot(WIDTH - 60, HEIGHT // 2 - 60, mode)
    else:
        player2 = Player(WIDTH - 60, HEIGHT // 2 - 60, (K_UP, K_DOWN))

    ball = Ball()
    score1 = 0
    score2 = 0

def draw_menu_background():
    window.fill(DARK)

    for star in stars:
        star.update()
        star.draw(window)

    if randint(0, 8) == 0:
        menu_particles.append(Particle(randint(0, WIDTH), HEIGHT))

    for p in menu_particles[:]:
        p.update()
        if p.life <= 0:
            menu_particles.remove(p)
        else:
            p.draw(window)

running = True

while running:

    mouse_pos = mouse.get_pos()
    update_music_volume()

    for e in event.get():

        if e.type == QUIT:
            running = False

        if e.type == KEYDOWN:

            if e.key == K_ESCAPE and state == "game":
                paused = not paused

            if e.key == K_m:
                state = "menu"
                paused = False

            if e.key == K_SPACE:
                if state in ("win", "lose"):
                    start_game(difficulty)
                    state = "game"

    if state == "menu":

        draw_menu_background()

        title = font_big.render("PING PONG", True, CYAN)
        window.blit(title, (310, 70))

        buttons = {
            "easy": (Rect(380, 170, 240, 45), (100, 255, 100)),
            "normal": (Rect(380, 240, 240, 45), (255, 255, 100)),
            "hard": (Rect(380, 310, 240, 45), (255, 120, 120)),
            "infinite": (Rect(380, 380, 240, 45), (120, 180, 255)),
            "2 players": (Rect(380, 450, 240, 45), (255, 180, 255)),
        }

        for name, (rect, color) in buttons.items():
            draw.rect(window, color, rect, border_radius=12)

            if rect.collidepoint(mouse_pos):
                draw.rect(window, WHITE, rect, 3, border_radius=12)

            text = font_small.render(name.upper(), True, (0, 0, 0))
            window.blit(text, (rect.x + 15, rect.y + 7))

        if mouse.get_pressed()[0]:
            for name, (rect, _) in buttons.items():
                if rect.collidepoint(mouse_pos):
                    difficulty = name
                    start_game(name)
                    state = "game"
                    paused = False

        display.update()
        clock.tick(FPS)
        continue

    if state == "game":

        window.fill(BLUE)

        for i in range(0, HEIGHT, 30):
            draw.rect(window, CYAN, (WIDTH // 2 - 3, i, 6, 18))

        if paused:
            pause_text = font_big.render("PAUSED", True, WHITE)
            info = font_small.render("Press ESC to continue", True, WHITE)
            window.blit(pause_text, (360, 220))
            window.blit(info, (325, 320))
            display.update()
            clock.tick(FPS)
            continue

        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)
            else:
                p.draw(window)

        player1.update()

        if isinstance(player2, Bot):
            player2.update(ball)
        else:
            player2.update()

        ball.update()

        ball.collide(player1)
        ball.collide(player2)

        if ball.rect.left <= 0:
            score2 += 1
            ball.reset()

        if ball.rect.right >= WIDTH:
            score1 += 1
            ball.reset()

        player1.draw(window)
        player2.draw(window)
        ball.draw(window)

        score_text = font_big.render(f"{score1}   {score2}", True, WHITE)
        window.blit(score_text, (400, 30))

        controls = font_small.render("P1: W/S   |   P2: ARROWS", True, WHITE)
        window.blit(controls, (20, 20))

        limit = settings[difficulty]["limit"]

        if score1 >= limit:
            state = "win"
        if score2 >= limit:
            state = "lose"

        display.update()
        clock.tick(FPS)

    if state == "win":
        window.fill(DARK)
        window.blit(font_big.render("PLAYER 1 WINS!", True, (100, 255, 120)), (250, 180))
        window.blit(font_small.render("Press SPACE to replay", True, WHITE), (340, 290))
        window.blit(font_small.render("Press M for menu", True, WHITE), (360, 330))
        display.update()
        clock.tick(FPS)

    if state == "lose":
        window.fill(DARK)
        window.blit(font_big.render("PLAYER 2 WINS!", True, (255, 120, 120)), (250, 180))
        window.blit(font_small.render("Press SPACE to replay", True, WHITE), (340, 290))
        window.blit(font_small.render("Press M for menu", True, WHITE), (360, 330))
        display.update()
        clock.tick(FPS)

quit()
