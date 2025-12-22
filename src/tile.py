import pygame
import os

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size, tile_type):
        super().__init__()
        self.z = 0
        self.image = pygame.Surface((size, size))
        
        full_path = os.path.join('assets', 'tiles')
        if tile_type == '1':
            img = pygame.image.load(os.path.join(full_path, "floor1.png")).convert()
        elif tile_type == '2':
            img = pygame.image.load(os.path.join(full_path, "floor2.png")).convert()
        elif tile_type == '3':
            img = pygame.image.load(os.path.join(full_path, "floor3.png")).convert()
        elif tile_type == '4':
            img = pygame.image.load(os.path.join(full_path, "inn1.png")).convert()
        elif tile_type == '5':
            img = pygame.image.load(os.path.join(full_path, "inn2.png")).convert()
        elif tile_type == '6':
            img = pygame.image.load(os.path.join(full_path, "inn3.png")).convert()
        elif tile_type == '7':
            img = pygame.image.load(os.path.join(full_path, "inn4.png")).convert()
        else:
            img = pygame.Surface((size, size))
            img.set_alpha(100)

        self.image = pygame.transform.scale(img, (size, size))
        self.rect = self.image.get_rect(topleft = pos)
