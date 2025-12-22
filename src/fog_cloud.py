import random

import pygame


class FogCloud(pygame.sprite.Sprite):
    def __init__(self, x, y, map_width, image, speed):
        super().__init__()
        self.z = 3
        self.map_width = map_width
        self.speed = speed
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, dt, camera_offset, viewport_size):
        self.rect.x += self.speed

        # loop around map
        if self.rect.left > self.map_width:
            self.rect.right = -random.randint(0, 200)
