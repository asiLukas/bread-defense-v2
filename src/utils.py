# @generated "partially" Gemini: Added docstrings and type annotations
import os
import random
from typing import Tuple

import pygame

from settings import BORDER_LEFT_INDEX, BORDER_RIGHT_INDEX, MAP_WIDTH


def generate_row(row_type: str) -> str:
    """
    Generates a comma-separated string representing a row in the tile map.

    Args:
        row_type: The type of row to generate ('sky', 'decor', 'ground', 'underground').

    Returns:
        A string of comma-separated tile IDs.
    """
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
        is_border = i in (BORDER_LEFT_INDEX, BORDER_RIGHT_INDEX)

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


def load_bg(
    filename: str, bg_size: Tuple[int, int], transparency: bool = False
) -> pygame.Surface:
    """
    Loads and scales a background image.

    Args:
        filename: Name of the file in assets/background.
        bg_size: Tuple (width, height) to scale the image to.
        transparency: Whether to use convert_alpha() or convert().

    Returns:
        Scaled pygame Surface.
    """
    path = os.path.join("assets", "background", filename)
    if transparency:
        img = pygame.image.load(path).convert_alpha()
    else:
        img = pygame.image.load(path).convert()
    return pygame.transform.scale(img, bg_size)


def draw_bg(
    surface: pygame.Surface,
    img: pygame.Surface,
    x_pos: float,
    y_pos: float,
    bg_w: int,
    screen_w: int,
) -> None:
    """
    Draws a parallax background image that loops.

    Args:
        surface: The target display surface.
        img: The background image surface.
        x_pos: Current X position (parallax offset).
        y_pos: Current Y position.
        bg_w: Width of the background image.
        screen_w: Width of the screen.
    """
    relative_x = x_pos % bg_w

    surface.blit(img, (relative_x - bg_w, y_pos))

    if relative_x < screen_w:
        surface.blit(img, (relative_x, y_pos))


SCORE_FILE = os.path.join("assets", "score")


def load_high_score() -> int:
    """Reads the high score from a local file."""
    if not os.path.exists(SCORE_FILE):
        return 0
    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            return int(f.read())
    except ValueError:
        return 0


def save_high_score(score: int) -> None:
    """Writes the new high score to a local file."""
    try:
        with open(SCORE_FILE, "w", encoding="utf-8") as f:
            f.write(str(score))
    except IOError:
        print("Could not save high score")
