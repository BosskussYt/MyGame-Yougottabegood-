import pygame
import requests
import random
import sys

# =========================
# SERVER URL
# =========================
API_URL = "https://mygame-yougottabegood.onrender.com"

# =========================
# LOGIN (einfach über Konsole)
# =========================
print("1 = Login")
print("2 = Register")
choice = input("Wähle: ")

username = input("Username: ")
password = input("Password: ")

if choice == "2":
    r = requests.post(API_URL + "/register", json={
        "username": username,
        "password": password
    })
else:
    r = requests.post(API_URL + "/login", json={
        "username": username,
        "password": password
    })

data = r.json()

if "token" not in data:
    print("Login fehlgeschlagen:", data)
    sys.exit()

TOKEN = data["token"]
print("Login erfolgreich!")

# =========================
# GAME SETUP
# =========================
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Online Arcade Game")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
RED = (255, 0, 0)

player_size = 50
player_pos = [WIDTH//2, HEIGHT-100]
base_speed = 6
player_speed = base_speed

enemy_size = 50
enemies = []
enemy_speed = 4

score = 0
font = pygame.font.SysFont("Arial", 30)

# =========================
# FUNCTIONS
# =========================
def spawn_enemy():
    if random.random() < 0.03:
        enemies.append([random.randint(0, WIDTH-enemy_size), 0])

def update_enemies():
    global score, enemy_speed
    for e in enemies[:]:
        e[1] += enemy_speed
        if e[1] > HEIGHT:
            enemies.remove(e)
            score += 1
            enemy_speed += 0.1

def collision():
    px, py = player_pos
    for ex, ey in enemies:
        if ex < px < ex+enemy_size or ex < px+player_size < ex+enemy_size:
            if ey < py < ey+enemy_size or ey < py+player_size < ey+enemy_size:
                return True
    return False

def send_score():
    try:
        requests.post(API_URL + "/score", json={
            "token": TOKEN,
            "score": score
        })
    except:
        print("Server nicht erreichbar")

def get_leaderboard():
    try:
        r = requests.get(API_URL + "/leaderboard")
        return r.json()
    except:
        return []

# =========================
# GAME LOOP
# =========================
running = True
game_over = False
show_lb = False
leaderboard = []

while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                # reset
                player_pos = [WIDTH//2, HEIGHT-100]
                enemies.clear()
                score = 0
                enemy_speed = 4
                game_over = False

            if event.key == pygame.K_TAB:
                show_lb = not show_lb
                if show_lb:
                    leaderboard = get_leaderboard()

    keys = pygame.key.get_pressed()

    if not game_over:
        if keys[pygame.K_LEFT]:
            player_pos[0] -= player_speed
        if keys[pygame.K_RIGHT]:
            player_pos[0] += player_speed

        spawn_enemy()
        update_enemies()

        if collision():
            send_score()
            game_over = True

        pygame.draw.rect(screen, WHITE, (*player_pos, player_size, player_size))
        for e in enemies:
            pygame.draw.rect(screen, RED, (*e, enemy_size, enemy_size))

        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (10, 10))

    else:
        text = font.render("GAME OVER - Press R", True, RED)
        screen.blit(text, (200, 250))

    # =========================
    # LEADERBOARD
    # =========================
    if show_lb:
        y = 50
        title = font.render("LEADERBOARD TOP 50", True, WHITE)
        screen.blit(title, (500, 10))

        for i, entry in enumerate(leaderboard[:50]):
            line = font.render(f"{i+1}. {entry['name']} - {entry['score']}", True, WHITE)
            screen.blit(line, (500, y))
            y += 25

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
