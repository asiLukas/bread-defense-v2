import pygame
import os


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size, tile_type, flip_x=False):
        super().__init__()
        self.z = 0
        self.image = pygame.Surface((size, size))
        full_path = os.path.join("assets", "tiles")
        tower_path = os.path.join("assets", "towers")

        self.tile_type = tile_type
        self.flip_x = flip_x
        self.price = 0
        self.is_buyable = False
        self.is_solid = True

        if int(tile_type) < 100:
            if tile_type == "1":
                img = pygame.image.load(os.path.join(full_path, "floor1.png")).convert()
            elif tile_type == "2":
                img = pygame.image.load(os.path.join(full_path, "floor2.png")).convert()
            elif tile_type == "3":
                img = pygame.image.load(os.path.join(full_path, "floor3.png")).convert()
            elif tile_type == "4":
                img = pygame.image.load(os.path.join(full_path, "inn1.png")).convert()
            elif tile_type == "5":
                img = pygame.image.load(os.path.join(full_path, "inn2.png")).convert()
            elif tile_type == "6":
                img = pygame.image.load(os.path.join(full_path, "inn3.png")).convert()
            elif tile_type == "7":
                img = pygame.image.load(os.path.join(full_path, "inn4.png")).convert()
            else:
                img = pygame.Surface((size, size))
                img.set_alpha(100)
            self.image = pygame.transform.scale(img, (size, size))
            self.rect = self.image.get_rect(topleft=pos)
            return

        # destroyed Towers
        if tile_type == "200":
            img = pygame.image.load(
                os.path.join(tower_path, "cannon_destroyed.png")
            ).convert_alpha()
            self.price = 50
            self.is_buyable = True
            self.is_solid = False
        elif tile_type == "201":
            img = pygame.image.load(
                os.path.join(tower_path, "archer1_destroyed.png")
            ).convert_alpha()
            self.price = 30
            self.is_buyable = True
            self.is_solid = False
        elif tile_type == "202":
            img = pygame.image.load(
                os.path.join(tower_path, "archer2_destroyed.png")
            ).convert_alpha()
            self.price = 70
            self.is_buyable = True
            self.is_solid = False
        # decor
        elif tile_type == "101":
            img = pygame.image.load(
                os.path.join(full_path, "grass_cliff.png")
            ).convert_alpha()
        elif tile_type == "102":
            img = pygame.image.load(
                os.path.join(full_path, "small_tree.png")
            ).convert_alpha()
        elif tile_type == "103":
            img = pygame.image.load(
                os.path.join(full_path, "bigger_tree.png")
            ).convert_alpha()
        elif tile_type == "104":
            img = pygame.image.load(os.path.join(full_path, "tree.png")).convert_alpha()
        elif tile_type == "105":
            img = pygame.image.load(
                os.path.join(full_path, "big_tree.png")
            ).convert_alpha()
        elif tile_type == "106":
            img = pygame.image.load(
                os.path.join(full_path, "big_cliff.png")
            ).convert_alpha()
        elif tile_type == "107":
            img = pygame.image.load(
                os.path.join(full_path, "small_cliff.png")
            ).convert_alpha()
        else:
            img = None

        self.image = img
        w, h = self.image.get_size()

        self.image = pygame.transform.scale(self.image, (int(w * 2), int(h * 2)))

        if flip_x:
            self.image = pygame.transform.flip(self.image, True, False)

        if tile_type in ["102", "103"]:
            self.rect = self.image.get_rect(midtop=pos)
        elif tile_type in ["200", "201", "202"]:
            # custom scaling for towers
            self.image = pygame.transform.scale(self.image, (int(w * 4), int(h * 4)))
            self.rect = self.image.get_rect(midbottom=pos)
        else:
            self.rect = self.image.get_rect(center=pos)
