# @generated "partially" Gemini: Added docstrings and type annotations
import pygame


class Bullet(pygame.sprite.Sprite):
    """
    Represents a projectile fired by the player or towers.
    """

    def __init__(
        self,
        x: int,
        y: int,
        direction: int,
        surf: pygame.Surface,
        damage: int = 10,
        gravity: float = 0,
    ) -> None:
        """
        Args:
            x: Spawn X coordinate.
            y: Spawn Y coordinate.
            direction: 1 for right, -1 for left.
            surf: Image surface for the bullet.
            damage: Damage dealt on impact.
            gravity: Vertical acceleration applied per frame.
        """
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
        self.vy: float = 0
        if self.gravity > 0:
            self.vy = -6  # Initial upward velocity for arced shots

        self.spawn_time = pygame.time.get_ticks()
        self.life_time = 1500

    def update(self, tiles: pygame.sprite.Group) -> None:
        """
        Moves the bullet and checks for collisions with walls.
        """
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
