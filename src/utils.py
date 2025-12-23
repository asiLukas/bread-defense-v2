import pygame

import random
import os

from settings import BORDER_LEFT_INDEX, BORDER_RIGHT_INDEX, MAP_WIDTH


def generate_row(row_type):
    row = []
    choices = []

    if row_type == "sky":
        choices = ["0"]
    elif row_type == "decor":
        choices = ["0"]
    elif row_type == "ground":
        choices = ["1", "2", "3"]
    elif row_type == "underground":
        choices = ["6", "7", "5"]

    for i in range(MAP_WIDTH):
        is_border = i == BORDER_LEFT_INDEX or i == BORDER_RIGHT_INDEX

        if is_border and row_type in ["sky", "decor"]:
            row.append("99")
            continue

        if row_type == "decor":
            if BORDER_LEFT_INDEX < i < BORDER_RIGHT_INDEX:
                if random.random() < 0.20:
                    decor = random.choice(
                        ["101", "102", "103", "104", "105", "106", "107"]
                    )
                    row.append(decor)
                else:
                    row.append("0")
            else:
                row.append("0")

        else:
            tile = random.choice(choices)
            row.append(tile)

    return ",".join(row)


tower_defense_map = [
    generate_row("sky"),
    generate_row("sky"),
    generate_row("sky"),
    generate_row("sky"),
    generate_row("sky"),
    generate_row("sky"),
    generate_row("sky"),
    generate_row("decor"),
    generate_row("ground"),
    generate_row("underground"),
    generate_row("underground"),
]


def load_bg(filename, bg, transparency=False):
    path = os.path.join("assets", "background", filename)
    if transparency:
        img = pygame.image.load(path).convert_alpha()
    else:
        img = pygame.image.load(path).convert()
    return pygame.transform.scale(img, bg)


def draw_bg(surface, img, x_pos, y_pos, bg_w, screen_w):
    relative_x = x_pos % bg_w

    surface.blit(img, (relative_x - bg_w, y_pos))

    if relative_x < screen_w:
        surface.blit(img, (relative_x, y_pos))
