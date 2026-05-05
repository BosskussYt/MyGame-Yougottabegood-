import pygame
import random
import requests

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arcade Shooter")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (100, 100, 100)

player_size = 50
base_speed = 7
max_speed = 14

# Gegner
enemy_size = 50
speed_increase = 0.3

API_URL = "http://localhost:5000/score"

font = pygame.font.SysFont("monospace", 35)


def reset_game():
    return {
        "player_pos": [WIDTH//2, HEIGHT-100],
        "player_speed": base_speed,
        "space_presses": 0,
        "enemy_list": [],
        "enemy_speed": 5,
        "score": 0,
        "game_over": False
    }


def spawn_enemies(enemy_list):
    if len(enemy_list) < 6:
        if random.random() < 0.1:
            enemy_list.append([random.randint(0, WIDTH-enemy_size), 0])


def update_enemies(state):
    for enemy in state["enemy_list"][:]:
        enemy[1] += state["enemy_speed"]
        if enemy[1] > HEIGHT:
            state["enemy_list"].remove(enemy)
            state["score"] += 1
            state["enemy_speed"] += speed_increase


def collision(player_pos, enemy_list):
    px, py = player_pos
    for ex, ey in enemy_list:
        if (ex < px < ex+enemy_size or ex < px+player_size < ex+enemy_size):
            if (ey < py < ey+enemy_size or ey < py+player_size < ey+enemy_size):
                return True
    return False


def draw_enemies(enemy_list):
    for enemy in enemy_list:
        pygame.draw.rect(screen, RED, (*enemy, enemy_size, enemy_size))


def send_score(score):
    try:
        requests.post(API_URL, json={"score": score})
    except:
        print("Server nicht erreichbar")


state = reset_game()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not state["game_over"]:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if state["space_presses"] < 10:
                        state["space_presses"] += 1
                    else:
                        state["enemy_speed"] = max(1, state["enemy_speed"] - 0.2)

                    state["player_speed"] = base_speed + (state["space_presses"] / 10) * (max_speed - base_speed)
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if WIDTH//2-100 < mx < WIDTH//2+100 and HEIGHT//2 < my < HEIGHT//2+50:
                    state = reset_game()

    screen.fill((0, 0, 0))

    if not state["game_over"]:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and state["player_pos"][0] > 0:
            state["player_pos"][0] -= state["player_speed"]
        if keys[pygame.K_RIGHT] and state["player_pos"][0] < WIDTH-player_size:
            state["player_pos"][0] += state["player_speed"]

        spawn_enemies(state["enemy_list"])
        update_enemies(state)

        if collision(state["player_pos"], state["enemy_list"]):
            send_score(state["score"])
            state["game_over"] = True

        pygame.draw.rect(screen, WHITE, (*state["player_pos"], player_size, player_size))
        draw_enemies(state["enemy_list"])

        score_text = font.render(f"Score: {state['score']}", True, WHITE)
        speed_text = font.render(f"Speed: {round(state['player_speed'],1)}", True, WHITE)

        screen.blit(score_text, (10, 10))
        screen.blit(speed_text, (10, 50))

    else:
        game_over_text = font.render("GAME OVER", True, RED)
        button_rect = pygame.Rect(WIDTH//2-100, HEIGHT//2, 200, 50)

        pygame.draw.rect(screen, GRAY, button_rect)
        button_text = font.render("RESET", True, WHITE)

        screen.blit(game_over_text, (WIDTH//2-120, HEIGHT//2-60))
        screen.blit(button_text, (WIDTH//2-60, HEIGHT//2+10))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()