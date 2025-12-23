# @generated "partially" Gemini: Added docstrings and type annotations
import random
from typing import Tuple

import pygame


class FogCloud(pygame.sprite.Sprite):
    """
    Ambient fog cloud that floats across the screen.
    """

    def __init__(
        self, x: int, y: int, map_width: int, image: pygame.Surface, speed: float
    ) -> None:
        super().__init__()
        self.z = 3
        self.map_width = map_width
        self.speed = speed
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(
        self,
        dt: float,
        camera_offset: pygame.math.Vector2,
        viewport_size: Tuple[int, int],
    ) -> None:
        """
        Moves the cloud and loops it around the map boundaries.
        Note: dt, camera_offset, and viewport_size are kept for interface compatibility
        but might not be used if logic is simple.
        """
        self.rect.x += self.speed

        # loop around map
        if self.rect.left > self.map_width:
            self.rect.right = -random.randint(0, 200)
