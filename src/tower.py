# @generated "partially" Gemini: Added docstrings and type annotations
import pygame
import os
from typing import Tuple, Callable


class Tower(pygame.sprite.Sprite):
    """
    Active defense tower that shoots at enemies.
    """

    def __init__(
        self,
        pos: Tuple[int, int],
        tower_type: str,
        flip_x: bool,
        create_bullet_callback: Callable,
    ) -> None:
        super().__init__()
        self.z = 1

        asset_name = ""
        self.damage = 0
        self.cooldown = 0
        self.range = 400
        self.bullet_gravity = 0.0
        self.bullet_offset = (0, 0)
        self.bullet_surf = None

        # upgrade stats
        self.level = 1
        self.max_level = 5
        self.upgrade_cost = 150

        # Tower stats configuration
        if tower_type == "200":
            asset_name = "cannon.png"
            self.damage = 30
            self.cooldown = 800
            self.bullet_speed = 10
            self.bullet_gravity = 0
            self.bullet_offset = (59, 39)
            self.bullet_surf = pygame.image.load(
                os.path.join("assets", "bullet.png")
            ).convert_alpha()
        elif tower_type == "201":
            asset_name = "archer1.png"
            self.damage = 10
            self.cooldown = 400
            self.bullet_speed = 12
            self.bullet_gravity = 1.5
            self.bullet_offset = (47, 11)
            self.bullet_surf = pygame.image.load(
                os.path.join("assets", "arrow.png")
            ).convert_alpha()
        elif tower_type == "202":
            asset_name = "archer2.png"
            self.damage = 20
            self.cooldown = 200
            self.bullet_speed = 15
            self.bullet_gravity = 1.8
            self.bullet_offset = (48, 13)
            self.bullet_surf = pygame.image.load(
                os.path.join("assets", "arrow.png")
            ).convert_alpha()

        img_path = os.path.join("assets", "towers", asset_name)
        self.original_image = pygame.image.load(img_path).convert_alpha()

        w, h = self.original_image.get_size()
        self.image = pygame.transform.scale(
            self.original_image, (int(w * 4), int(h * 4))
        )

        self.flip_x = flip_x
        if self.flip_x:
            self.image = pygame.transform.flip(self.image, True, False)
            self.direction = -1
        else:
            self.direction = 1

        self.rect = self.image.get_rect(midbottom=pos)

        self.create_bullet = create_bullet_callback
        self.last_shot_time = pygame.time.get_ticks()

    def update(self, enemies: pygame.sprite.Group) -> None:
        """
        Finds the closest enemy and shoots if cooldown is ready.
        """
        current_time = pygame.time.get_ticks()

        if current_time - self.last_shot_time >= self.cooldown:
            for enemy in enemies:
                dist = abs(enemy.rect.centerx - self.rect.centerx)

                if self.flip_x:  # left
                    facing_target = enemy.rect.centerx < self.rect.centerx
                else:  # right
                    facing_target = enemy.rect.centerx > self.rect.centerx

                if (
                    dist <= self.range
                    and facing_target
                    and not getattr(enemy, "is_dead", False)
                ):
                    self.shoot()
                    self.last_shot_time = current_time
                    break

    def shoot(self) -> None:
        """Calculates spawn position and triggers the bullet creation callback."""
        ox, oy = self.bullet_offset
        scaled_ox = ox * 4
        scaled_oy = oy * 4

        spawn_y = self.rect.top + scaled_oy

        if self.flip_x:
            img_width = self.original_image.get_width() * 4
            spawn_x = self.rect.left + (img_width - scaled_ox)
        else:
            spawn_x = self.rect.left + scaled_ox

        if self.bullet_surf:
            self.create_bullet(
                spawn_x,
                spawn_y,
                self.direction,
                self.bullet_surf,
                self.damage,
                self.bullet_gravity,
            )

    def upgrade(self) -> None:
        """Increases tower stats and upgrade cost."""
        if self.level < self.max_level:
            self.level += 1
            self.damage = int(self.damage * 1.3)
            self.cooldown = max(100, int(self.cooldown * 0.9))
            self.upgrade_cost = int(self.upgrade_cost * 1.5)
