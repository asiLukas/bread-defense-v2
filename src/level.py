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
from settings import (
    TILE_SIZE,
    DAY_CYCLE_LENGTH,
    NIGHT_START_THRESHOLD,
    NIGHT_END_THRESHOLD,
    MAX_DARKNESS,
    CELEBRATION_DURATION,
)


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
        self.map_width = len(level_data[0].split(",")) * TILE_SIZE
        self.map_height = len(level_data) * TILE_SIZE

        self.setup_level(level_data)

        self.rain = Rain(self.display_surface)

        font_path = os.path.join("assets", "font.ttf")
        self.font = pygame.font.Font(font_path, 74)
        self.ui_font = pygame.font.Font(font_path, 20)

        # day/night counter
        self.day_timer = 0
        self.current_darkness = 0
        self.is_night = False
        self.day_count = 1

        # celebration Logic
        self.show_celebration = False
        self.celebration_timer = 0

        # Overlays
        self.dark_overlay = pygame.Surface(self.display_surface.get_size())
        self.dark_overlay.fill((10, 10, 35))  # deep blue/black night tint

        self.spawn_timer = 0
        self.spawn_cooldown = 120

    def generate_cloud_cache(self):
        cache = []
        particle_sys = particlepy.particle.ParticleSystem()

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

        self.day_timer = 0
        self.day_count = 1
        self.is_night = False
        self.show_celebration = True
        self.celebration_timer = CELEBRATION_DURATION

        for row_index, row in enumerate(layout):
            row_values = row.split(",")
            for col_index, val in enumerate(row_values):
                val = val.strip()
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if val == "99":
                    tile = Tile((x, y), TILE_SIZE, val)
                    self.tiles.add(tile)

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

        # Center spawn calculation
        center_x = self.map_width // 2
        ground_y = 8 * TILE_SIZE

        p = Player(center_x, ground_y, 1)
        self.player.add(p)
        self.visible_sprites.add(p)

        # Destroyed towers: (offset_x, tile_type, flip_x)
        left_towers = [
            (-800, "200", True),   # cannon
            (-1600, "201", True),  # archer1
            (-2400, "202", True),  # archer2
        ]
        right_towers = [
            (800, "200", False),
            (1600, "201", False),
            (2400, "202", False),
        ]

        for offset, t_type, flip in left_towers + right_towers:
            tower = Tile((center_x + offset, ground_y), TILE_SIZE, t_type, flip_x=flip)
            self.visible_sprites.add(tower)

        num_clouds = self.map_width // 150
        for _ in range(num_clouds):
            cx = random.randint(0, self.map_width)
            cy = random.randint(0, self.map_height)
            image = random.choice(self.cloud_surf_cache)
            speed = random.uniform(0.3, 0.8)
            cloud = FogCloud(cx, cy, self.map_width, image, speed)
            self.clouds.add(cloud)
            self.visible_sprites.add(cloud)

    def day_night_cycle(self):
        prev_day_index = self.day_timer // DAY_CYCLE_LENGTH

        self.day_timer += 1

        curr_day_index = self.day_timer // DAY_CYCLE_LENGTH

        if curr_day_index > prev_day_index:
            self.day_count += 1
            self.show_celebration = True
            self.celebration_timer = CELEBRATION_DURATION

        progress = (self.day_timer % DAY_CYCLE_LENGTH) / DAY_CYCLE_LENGTH

        if progress < NIGHT_START_THRESHOLD:
            # day
            target_alpha = 0
            self.is_night = False
        elif progress < (NIGHT_START_THRESHOLD + 0.1):
            # dusk
            transition = (progress - NIGHT_START_THRESHOLD) * 10
            target_alpha = int(transition * MAX_DARKNESS)
            self.is_night = False
        elif progress < NIGHT_END_THRESHOLD:
            # night
            target_alpha = MAX_DARKNESS
            self.is_night = True
        else:
            # Dawn
            transition = (progress - NIGHT_END_THRESHOLD) * 10
            target_alpha = int(MAX_DARKNESS - (transition * MAX_DARKNESS))
            self.is_night = False

        self.current_darkness = target_alpha
        self.dark_overlay.set_alpha(self.current_darkness)

    def spawn_night_enemies(self):
        if self.is_night and not self.player.sprite.is_dead:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_cooldown:
                self.spawn_timer = 0
                x_pos = random.randint(200, self.map_width - 200)
                y_pos = -100
                enemy = Enemy(x_pos, y_pos, "enemy01", 4)
                self.enemies.add(enemy)
                self.visible_sprites.add(enemy)

    def draw_ui(self):
        counter_text = f"day: {self.day_count}"
        text_surf = self.ui_font.render(counter_text, True, (255, 255, 255))

        screen_w, screen_h = self.display_surface.get_size()
        text_rect = text_surf.get_rect(bottomright=(screen_w, screen_h))

        shadow_surf = self.ui_font.render(counter_text, True, (0, 0, 0))
        shadow_rect = text_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2

        self.display_surface.blit(shadow_surf, shadow_rect)

        # morning celeb
        if self.show_celebration:
            self.celebration_timer -= 1
            if self.celebration_timer <= 0:
                self.show_celebration = False
            else:
                msg = (
                    f"survived day {self.day_count - 1}"
                    if self.day_count > 1
                    else "day 1"
                )
                big_text = self.font.render(msg, True, (255, 215, 0))
                big_rect = big_text.get_rect(
                    center=(screen_w // 2, screen_h // 2 - 100)
                )

                big_shadow = self.font.render(msg, True, (0, 0, 0))
                big_shadow_rect = big_rect.copy()
                big_shadow_rect.center = (screen_w // 2 + 4, screen_h // 2 - 96)

                self.display_surface.blit(big_shadow, big_shadow_rect)
                self.display_surface.blit(big_text, big_rect)

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
        self.day_night_cycle()
        self.spawn_night_enemies()

        self.visible_sprites.custom_draw(self.player.sprite)  #

        if self.current_darkness > 0:
            self.display_surface.blit(self.dark_overlay, (0, 0))

        self.rain.update()
        self.rain.draw()

        self.draw_ui()

        if self.check_game_over():
            return

        self.enemies.update(self.tiles, self.player.sprite)
        self.player.sprite.update(self.tiles)
        self.clouds.update(1.0, None, None)

        hits = pygame.sprite.spritecollide(self.player.sprite, self.enemies, False)
        if hits:
            self.player.sprite.get_damage(20)
