import pygame


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, surf, damage=10, gravity=0):
        super().__init__()
        self.z = 2

        scale_factor = 4
        w, h = surf.get_size()
        self.image = pygame.transform.scale(surf, (w * scale_factor, h * scale_factor))

        if direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = 12
        self.damage = damage

        self.gravity = gravity
        self.vy = 0
        if self.gravity > 0:
            self.vy = -6

        self.spawn_time = pygame.time.get_ticks()
        self.life_time = 1500

    def update(self, tiles):
        self.rect.x += self.direction * self.speed

        if self.gravity > 0:
            self.vy += self.gravity
            self.rect.y += self.vy

        for tile in tiles:
            # Only collide with solid tiles
            if getattr(tile, "is_solid", True):
                if tile.rect.colliderect(self.rect):
                    self.kill()

        if pygame.time.get_ticks() - self.spawn_time > self.life_time:
            self.kill()

        if self.rect.y > 2000:
            self.kill()
