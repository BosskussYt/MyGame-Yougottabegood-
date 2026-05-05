import pygame
import requests
import random
import sys

API = "https://mygame-yougottabegood.onrender.com"

# -------------------------
# LOGIN
# -------------------------
print("1 Login")
print("2 Register")

mode = input("> ")
name = input("Username: ")
pw = input("Password: ")

if mode == "2":
    r = requests.post(API + "/register", json={"username": name, "password": pw})
else:
    r = requests.post(API + "/login", json={"username": name, "password": pw})

data = r.json()

if "token" not in data:
    print("Fehler:", data)
    sys.exit()

TOKEN = data["token"]
print("Login OK")

# -------------------------
# GAME
# -------------------------
pygame.init()

W, H = 800, 600
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

player = [400, 500]
enemies = []

score = 0
speed = 5

font = pygame.font.SysFont("Arial", 30)

def spawn():
    if random.random() < 0.03:
        enemies.append([random.randint(0, W-50), 0])

def move():
    global score, speed
    for e in enemies[:]:
        e[1] += speed
        if e[1] > H:
            enemies.remove(e)
            score += 1
            speed += 0.1

def hit():
    px, py = player
    for ex, ey in enemies:
        if ex < px < ex+50 and ey < py < ey+50:
            return True
    return False

def send():
    requests.post(API + "/score", json={
        "token": TOKEN,
        "score": score
    })

run = True
game_over = False

while run:
    screen.fill((0,0,0))

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False

        if game_over and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_r:
                player = [400, 500]
                enemies = []
                score = 0
                speed = 5
                game_over = False

    keys = pygame.key.get_pressed()

    if not game_over:
        if keys[pygame.K_LEFT]:
            player[0] -= 7
        if keys[pygame.K_RIGHT]:
            player[0] += 7

        spawn()
        move()

        if hit():
            send()
            game_over = True

        pygame.draw.rect(screen, (255,255,255), (*player, 50, 50))

        for e in enemies:
            pygame.draw.rect(screen, (255,0,0), (*e, 50, 50))

        txt = font.render(f"Score: {score}", True, (255,255,255))
        screen.blit(txt, (10,10))

    else:
        txt = font.render("GAME OVER - R to restart", True, (255,0,0))
        screen.blit(txt, (200,300))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
