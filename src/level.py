import os
import random

import pygame

import particlepy.particle
import particlepy.shape

from camera_group import CameraGroup
from fog_cloud import FogCloud
from rain import Rain
from tile import Tile
from player import Player
from enemy import Enemy
from settings import TILE_SIZE


class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface

        self.visible_sprites = CameraGroup()
        self.tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.clouds = pygame.sprite.Group()

        self.cloud_surf_cache = self.generate_cloud_cache()

        self.level_data = level_data
        self.setup_level(level_data)

        self.rain = Rain(self.display_surface)

        font_path = os.path.join("assets", "font.ttf")
        self.font = pygame.font.Font(font_path, 74)

    def generate_cloud_cache(self):
        cache = []
        particle_sys = particlepy.particle.ParticleSystem()

        # create the soft "puff" texture once
        puff_radius = 40
        puff_padding = 20
        puff_size = (puff_radius + puff_padding) * 2
        puff_surf = pygame.Surface((puff_size, puff_size), pygame.SRCALPHA)
        center = puff_size // 2
        for r in range(puff_radius, 0, -2):
            pygame.draw.circle(puff_surf, (255, 255, 255, 3), (center, center), r)

        for _ in range(10):
            w = random.randint(300, 500)
            h = random.randint(150, 250)
            cloud_image = pygame.Surface((w, h), pygame.SRCALPHA)

            for _ in range(45):
                size = random.randint(60, 100)
                shape = particlepy.shape.Image(
                    surface=puff_surf, size=(size, size), alpha=random.randint(50, 150)
                )
                p = particlepy.particle.Particle(
                    shape=shape,
                    position=(random.randint(20, w - 20), random.randint(20, h - 20)),
                    velocity=(0, 0),
                    delta_radius=0,
                )
                particle_sys.emit(p)

            particle_sys.make_shape()
            particle_sys.render(cloud_image)
            particle_sys.clear()
            cache.append(cloud_image)

        return cache

    def setup_level(self, layout):
        self.visible_sprites.empty()
        self.tiles.empty()
        self.enemies.empty()
        self.player.empty()
        self.clouds.empty()

        enemy_map = {
            "e01": "enemy01",
            "e02": "enemy02",
            "e03": "enemy03",
            "e04": "enemy04",
            "e05": "enemy05",
            "e06": "enemy06",
        }

        map_width = len(layout[0].split(",")) * TILE_SIZE
        map_height = len(layout) * TILE_SIZE

        for row_index, row in enumerate(layout):
            row_values = row.split(",")
            for col_index, val in enumerate(row_values):
                val = val.strip()
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if val == "99":
                    tile = Tile((x, y), TILE_SIZE, val)
                    self.tiles.add(tile)  # Add to collision group

                if val in [f"{i}" for i in range(1, 9)]:
                    tile = Tile((x, y), TILE_SIZE, val)
                    self.tiles.add(tile)
                    self.visible_sprites.add(tile)
                elif val in [f"{i}" for i in range(100, 109)]:
                    tile = Tile((x, y), TILE_SIZE, val)
                    self.visible_sprites.add(tile)

                elif val in enemy_map:
                    enemy_variant = enemy_map[val]
                    enemy = Enemy(x, y, enemy_variant, 4)
                    self.enemies.add(enemy)
                    self.visible_sprites.add(enemy)

        p = Player(5000, 1000, 1)
        self.player.add(p)
        self.visible_sprites.add(p)

        num_clouds = map_width // 150
        for _ in range(num_clouds):
            cx = random.randint(0, map_width)
            cy = random.randint(0, map_height)
            image = random.choice(self.cloud_surf_cache)
            speed = random.uniform(0.3, 0.8)
            cloud = FogCloud(cx, cy, map_width, image, speed)
            self.clouds.add(cloud)
            self.visible_sprites.add(cloud)

    def check_game_over(self):
        player = self.player.sprite
        if player.is_dead:
            overlay = pygame.Surface(self.display_surface.get_size())
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.display_surface.blit(overlay, (0, 0))

            text_surf = self.font.render("GAME OVER", True, "Red")
            text_rect = text_surf.get_rect(
                center=(
                    self.display_surface.get_width() // 2,
                    self.display_surface.get_height() // 2 - 50,
                )
            )
            self.display_surface.blit(text_surf, text_rect)

            restart_surf = self.font.render("Press 'R' to Restart", True, "White")
            restart_rect = restart_surf.get_rect(
                center=(
                    self.display_surface.get_width() // 2,
                    self.display_surface.get_height() // 2 + 50,
                )
            )
            self.display_surface.blit(restart_surf, restart_rect)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.setup_level(self.level_data)
            return True
        return False

    def run(self):
        self.visible_sprites.custom_draw(self.player.sprite)

        self.rain.update()
        self.rain.draw()

        if self.check_game_over():
            return

        self.enemies.update(self.tiles, self.player.sprite)
        self.player.sprite.update(self.tiles)
        self.clouds.update(1.0, None, None)

        hits = pygame.sprite.spritecollide(self.player.sprite, self.enemies, False)
        if hits:
            self.player.sprite.get_damage(20)
