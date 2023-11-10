import sys

import pygame
import json
import time
import tkinter as tk
from tkinter import filedialog
import numpy as np

WINDOWS_SIZE = 1300

TILE_COLOR = (131, 137, 141)
BLOCK_SIZE = 40
PADDING = 3 * BLOCK_SIZE
BACKGROUND_COLOR = (123, 149, 128)

GREEN_DOR_COLOR = 0
YELLOW_DOR_COLOR = 0
RED_DOR_COLOR = 0

BOARDER_COLOR = (0, 0, 0)
BOX_COLOR = (100, 100, 100)
TELEPORT_COLOR = (0, 0, 0)
WINDOWS_PADDING = 20 * BLOCK_SIZE
TIME_SLEEP = 0.5

GEMS_PATH = [
    "assets/yellow_dimond.png",
    "assets/green_dimond.png",
    "assets/red_dimond.png",
    "assets/blue_dimond.png"

]
AGENTS_PATH = [
    "assets/agent_green.png",
    "assets/agent_purple.png"

]
KEY_PATH = {
    "g": "assets/green_key.png",
    "y": "assets/yellow_key.png",
    "r": "assets/red_key.png",
}


def get_game_log_json():
    root = tk.Tk()
    root.withdraw()
    file_name = filedialog.askopenfilename()
    try:
        with open(file_name) as file:
            content = json.load(file)
        return content
    except:
        return None


def draw_wall(pygame, screen, x, y):
    image = pygame.image.load("assets/wall.png")
    image = pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE))
    X = PADDING + x * BLOCK_SIZE
    Y = PADDING + y * BLOCK_SIZE
    screen.blit(image, (X, Y))


def draw_barbed(pygame, screen, x, y):
    image = pygame.image.load("assets/barbed.svg")
    image = pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE))
    X = PADDING + x * BLOCK_SIZE
    Y = PADDING + y * BLOCK_SIZE
    screen.blit(image, (X, Y))


def draw_player(pygame, screen, x, y, agent_index):
    # image = pygame.image.load(io.BytesIO(base64.b64decode(GEM)))
    image = pygame.image.load(AGENTS_PATH[agent_index])
    image = pygame.transform.scale(image, (int(0.9 * BLOCK_SIZE), int(0.9 * BLOCK_SIZE)))
    X = PADDING + x * BLOCK_SIZE
    Y = PADDING + y * BLOCK_SIZE
    screen.blit(image, (X, Y))
    # screen.blit(image, (X, Y),)


def draw_teleport(pygame, screen, x, y):
    X = PADDING + x * BLOCK_SIZE + BLOCK_SIZE // 2
    Y = PADDING + y * BLOCK_SIZE + BLOCK_SIZE // 2
    pygame.draw.circle(screen, TELEPORT_COLOR, (X, Y), (6 * BLOCK_SIZE) // 13)


def draw_gem(pygame, screen, x, y, gem_index):
    image = pygame.image.load(GEMS_PATH[gem_index])

    image = pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE))
    X = PADDING + x * BLOCK_SIZE
    Y = PADDING + y * BLOCK_SIZE

    # load_svg("assets/blue_dimond.svg", screen, (x, y), (BLOCK_SIZE, BLOCK_SIZE))
    screen.blit(image, (X, Y))


def draw_key(pygame, screen, x, y, key_character):
    image = pygame.image.load(KEY_PATH[key_character])
    image = pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE))
    X = PADDING + x * BLOCK_SIZE
    Y = PADDING + y * BLOCK_SIZE
    # load_svg("assets/blue_dimond.svg", screen, (x, y), (BLOCK_SIZE, BLOCK_SIZE))
    screen.blit(image, (X, Y))


def draw_DOOR(pygame, screen, x, y, COLORE):
    X = x * BLOCK_SIZE + PADDING
    Y = y * BLOCK_SIZE + PADDING
    center = (X + BLOCK_SIZE + BLOCK_SIZE // 2, Y + BLOCK_SIZE + BLOCK_SIZE // 2)
    rect = pygame.Rect(X, Y, BLOCK_SIZE, BLOCK_SIZE)
    pygame.draw.rect(screen, COLORE, rect, 3)


def draw_characters(pygame, screen, x, y, characters):
    if "T" in characters:
        draw_teleport(pygame, screen, x, y)

    if "W" in characters:
        draw_wall(pygame, screen, x, y)
    if "1" in characters:
        draw_gem(pygame, screen, x, y, 0)

    if "2" in characters:
        draw_gem(pygame, screen, x, y, 1)
    if "3" in characters:
        draw_gem(pygame, screen, x, y, 2)

    if "4" in characters:
        draw_gem(pygame, screen, x, y, 3)

    if "g" in characters:
        draw_key(pygame, screen, x, y, "g")
    if "y" in characters:
        draw_key(pygame, screen, x, y, "y")
    if "r" in characters:
        draw_key(pygame, screen, x, y, "r")

    if "G" in characters:
        draw_DOOR(pygame, screen, x, y, (30, 250, 8))
    if "Y" in characters:
        draw_DOOR(pygame, screen, x, y, (239, 250, 8))
    if "R" in characters:
        draw_DOOR(pygame, screen, x, y, (250, 63, 8))

    if "*" in characters:
        draw_barbed(pygame, screen, x, y)

    if "A" in characters:
        draw_player(pygame, screen, x, y, 0)

    if "B" in characters:
        draw_player(pygame, screen, x, y, 1)


def write_information(pygame, screen, start_address, agent_information, report):
    X, Y = start_address
    font = pygame.font.Font('freesansbold.ttf', BLOCK_SIZE // 3)

    Text = f" {report}"
    text = font.render(Text, True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.centery = PADDING - BLOCK_SIZE
    textRect.x = X
    screen.blit(text, textRect)

    for index, info in enumerate(agent_information):
        Text = f"agent {index + 1} : score = {info['score']}   hits={info['hit_hurts_count']} " \
               f" gems= {[info['gem1'], info['gem2'], info['gem3'], info['gem4']]}"

        text = font.render(Text, True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.centery = Y + index * BLOCK_SIZE
        textRect.x = X

        screen.blit(text, textRect)


def show(json_content):
    global BLOCK_SIZE
    global PADDING

    time_sleep = TIME_SLEEP
    pause = False
    stop = False
    height, width = np.array(json_content[0]["map"]).shape
    BLOCK_SIZE = WINDOWS_SIZE // (max(height, width) + 20)
    PADDING = 3 * BLOCK_SIZE

    HEIGHT, WIDTH = height * BLOCK_SIZE, width * BLOCK_SIZE
    WIDTH = max(11 * BLOCK_SIZE, WIDTH)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH + 2 * PADDING, HEIGHT + 2 * PADDING))
    grid_rect = pygame.Rect(PADDING, PADDING, WIDTH, HEIGHT)

    i = 0
    while True:
        if stop:
            time.sleep(time_sleep)
            continue
        screen.fill(BACKGROUND_COLOR)
        screen.fill(color=TILE_COLOR, rect=grid_rect)

        current_map = json_content[i]["map"]
        for x in range(width):
            for y in range(height):
                X = x * BLOCK_SIZE + PADDING
                Y = y * BLOCK_SIZE + PADDING
                center = (X + BLOCK_SIZE + BLOCK_SIZE // 2, Y + BLOCK_SIZE + BLOCK_SIZE // 2)

                tile = current_map[y][x]
                rect = pygame.Rect(X, Y, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, BOARDER_COLOR, rect, 1)
                draw_characters(pygame, screen, x, y, tile)

        write_information(pygame, screen, (PADDING, HEIGHT + PADDING + BLOCK_SIZE), json_content[i]["agents_info"],
                          json_content[i]["report"])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if time_sleep >= 0.2:
                        time_sleep -= 0.1

                if event.key == pygame.K_w:
                    if time_sleep <= 2:
                        time_sleep += 0.1

                if event.key == pygame.K_s:
                    pause = not pause

                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_r:
                    i = -1

                if event.key == pygame.K_b:
                    if BLOCK_SIZE < 100:
                        BLOCK_SIZE += 5
                        PADDING = 3 * BLOCK_SIZE

                        HEIGHT, WIDTH = height * BLOCK_SIZE, width * BLOCK_SIZE
                        WIDTH = max(11 * BLOCK_SIZE, WIDTH)

                        pygame.init()
                        screen = pygame.display.set_mode((WIDTH + 2 * PADDING, HEIGHT + 2 * PADDING))
                        grid_rect = pygame.Rect(PADDING, PADDING, WIDTH, HEIGHT)

                if event.key == pygame.K_n:
                    if 10 < BLOCK_SIZE:
                        BLOCK_SIZE -= 5
                        PADDING = 3 * BLOCK_SIZE
                        HEIGHT, WIDTH = height * BLOCK_SIZE, width * BLOCK_SIZE
                        WIDTH = max(11 * BLOCK_SIZE, WIDTH)

                        pygame.init()
                        screen = pygame.display.set_mode((WIDTH + 2 * PADDING, HEIGHT + 2 * PADDING))
                        grid_rect = pygame.Rect(PADDING, PADDING, WIDTH, HEIGHT)
        if pause:
            continue

        pygame.display.update()
        time.sleep(time_sleep)
        if i < len(json_content) - 1:
            i += 1


if __name__ == '__main__':
    json_content = get_game_log_json()
    if json_content is not None:
        show(json_content)
