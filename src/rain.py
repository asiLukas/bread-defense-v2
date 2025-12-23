# @generated "partially" Gemini: Added docstrings and type annotations
import random
from typing import List

import pygame


class Rain:
    """
    Manages and renders rain particles directly on the surface.
    """

    def __init__(self, surface: pygame.Surface) -> None:
        self.display_surface = surface
        self.width = surface.get_width()
        self.height = surface.get_height()
        self.drops: List[List[float]] = []  # [x, y, length, speed, color_tuple]
        self.create_drops()

    def create_drops(self) -> None:
        """Initializes a set of rain drops."""
        for _ in range(20):
            x = random.randint(0, self.width)
            y = random.randint(-self.height, self.height)

            length = random.randint(5, 15)
            speed = random.randint(4, 9)

            alpha = random.randint(50, 150)
            color = (200, 240, 255, alpha)

            self.drops.append([x, y, length, speed, color])

    def update(self) -> None:
        """Moves drops down and resets them when they leave the screen."""
        for drop in self.drops:
            drop[1] += drop[3]  # y += speed

            if drop[1] > self.height:
                # reset far above screen to create uneven timing/gaps
                drop[1] = random.randint(-500, -50)
                drop[0] = random.randint(0, self.width)
                # randomize speed slightly on reset
                drop[3] = random.randint(4, 9)

    def draw(self) -> None:
        """Draws the rain drops as lines."""
        for drop in self.drops:
            x, y, length, _, color = drop

            start_pos = (x, int(y))
            end_pos = (x, int(y + length))

            # Draw directly to the display surface
            pygame.draw.line(self.display_surface, color, start_pos, end_pos, 1)
