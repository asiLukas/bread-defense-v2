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
from bullet import Bullet
from tower import Tower
from settings import (
    TILE_SIZE,
    DAY_CYCLE_LENGTH,
    NIGHT_START_THRESHOLD,
    NIGHT_END_THRESHOLD,
    MAX_DARKNESS,
    CELEBRATION_DURATION,
    BORDER_LEFT_INDEX,
    BORDER_RIGHT_INDEX,
)


class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface

        self.visible_sprites = CameraGroup()
        self.tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.clouds = pygame.sprite.Group()

        self.cloud_surf_cache = self.generate_cloud_cache()

        self.level_data = level_data
        self.map_width = len(level_data[0].split(",")) * TILE_SIZE
        self.map_height = len(level_data) * TILE_SIZE

        # wave management
        self.night_enemy_queue = []
        self.wave_generated = False
        self.spawn_cooldown = 120

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

        # Interaction
        self.mouse_pressed_prev = False

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
        self.bullets.empty()
        self.towers.empty()
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

        self.night_enemy_queue = []
        self.wave_generated = False

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
                    # Calculate facing
                    facing = True
                    if x > self.map_width // 2:
                        facing = False
                    if enemy_variant in ["enemy_06", "enemy_02"]:
                        enemy = Enemy(x, y, enemy_variant, 6, facing_right=facing)
                    else:
                        enemy = Enemy(x, y, enemy_variant, 4, facing_right=facing)
                    self.enemies.add(enemy)
                    self.visible_sprites.add(enemy)

        # center spawn calculation
        center_x = self.map_width // 2
        ground_y = 8 * TILE_SIZE

        p = Player(center_x, ground_y, 1)
        self.player.add(p)
        self.visible_sprites.add(p)

        # Destroyed towers
        left_towers = [
            (-800, "200", True),  # cannon
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
            # Add to tiles too so we can find it easily for interaction
            self.tiles.add(tower)

        num_clouds = self.map_width // 150
        for _ in range(num_clouds):
            cx = random.randint(0, self.map_width)
            cy = random.randint(0, self.map_height)
            image = random.choice(self.cloud_surf_cache)
            speed = random.uniform(0.3, 0.8)
            cloud = FogCloud(cx, cy, self.map_width, image, speed)
            self.clouds.add(cloud)
            self.visible_sprites.add(cloud)

    def create_bullet(self, x, y, direction, surf, damage=10, gravity=0):
        bullet = Bullet(x, y, direction, surf, damage, gravity)
        self.bullets.add(bullet)
        self.visible_sprites.add(bullet)

    def generate_night_queue(self):
        self.night_enemy_queue = []
        day = self.day_count

        # difficulty scaling
        num_enemies = 4 + int(day * 2.5)
        health_mult = 1.0 + (day * 0.1)
        damage_mult = 1.0 + (day * 0.05)

        # enemy pool management
        pool = ["enemy01", "enemy02", "enemy03", "enemy04", "enemy05", "enemy06"]

        for _ in range(num_enemies):
            variant = random.choice(pool)
            self.night_enemy_queue.append((variant, health_mult, damage_mult))

        # we target spawning en within 80% of night (1200 frames)
        total_spawn_time = 1200
        self.spawn_cooldown = max(20, total_spawn_time // num_enemies)
        self.spawn_timer = self.spawn_cooldown

    def day_night_cycle(self):
        prev_day_index = self.day_timer // DAY_CYCLE_LENGTH

        self.day_timer += 1

        curr_day_index = self.day_timer // DAY_CYCLE_LENGTH

        if curr_day_index > prev_day_index:
            self.day_count += 1
            self.show_celebration = True
            self.celebration_timer = CELEBRATION_DURATION
            self.wave_generated = False  # reset for new day

        progress = (self.day_timer % DAY_CYCLE_LENGTH) / DAY_CYCLE_LENGTH

        if progress < NIGHT_START_THRESHOLD:
            # day
            target_alpha = 0
            self.is_night = False
        elif progress < (NIGHT_START_THRESHOLD + 0.1):
            # dusk
            transition = (progress - NIGHT_START_THRESHOLD) * 10
            target_alpha = int(transition * MAX_DARKNESS)
            self.is_night = True
        elif progress < NIGHT_END_THRESHOLD:
            # night
            target_alpha = MAX_DARKNESS
            self.is_night = True

            # generate wave if first time entering night this day
            if not self.wave_generated:
                self.generate_night_queue()
                self.wave_generated = True

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

                if self.night_enemy_queue:
                    variant, hp_m, dmg_m = self.night_enemy_queue.pop(0)

                    min_x = BORDER_LEFT_INDEX * TILE_SIZE + 10 * TILE_SIZE
                    max_x = BORDER_RIGHT_INDEX * TILE_SIZE - 10 * TILE_SIZE
                    x = random.randint(min_x, max_x)
                    y = -100

                    # Calculate facing
                    facing = True
                    if x > self.map_width // 2:
                        facing = False

                    if variant in ["enemy_06", "enemy_02"]:
                        enemy = Enemy(
                            x, y, variant, 6, hp_m, dmg_m, facing_right=facing
                        )
                    else:
                        enemy = Enemy(
                            x, y, variant, 4, hp_m, dmg_m, facing_right=facing
                        )
                    self.enemies.add(enemy)
                    self.visible_sprites.add(enemy)

    def handle_interaction(self):
        mouse_pos = pygame.mouse.get_pos()
        # adjust mouse pos for camera offset
        world_x = mouse_pos[0] + self.visible_sprites.offset.x
        world_y = mouse_pos[1] + self.visible_sprites.offset.y
        mouse_world_pos = (world_x, world_y)

        mouse_pressed = pygame.mouse.get_pressed()[0]

        # check hover for prices (Destroyed Towers)
        hovered_obj = None

        # Check tiles (Destroyed towers)
        for sprite in self.tiles:
            if (
                sprite.rect.collidepoint(mouse_world_pos)
                and hasattr(sprite, "is_buyable")
                and sprite.is_buyable
            ):
                hovered_obj = sprite
                break

        # Check built towers (Upgrades)
        if not hovered_obj:
            for sprite in self.towers:
                if sprite.rect.collidepoint(mouse_world_pos):
                    hovered_obj = sprite
                    break

        # buying/upgrading logic
        if mouse_pressed and not self.mouse_pressed_prev:
            if hovered_obj:
                # If it's a destroyed tower (Tile)
                if isinstance(hovered_obj, Tile):
                    if self.player.sprite.money >= hovered_obj.price:
                        self.player.sprite.money -= hovered_obj.price

                        # create repaired tower
                        new_tower = Tower(
                            hovered_obj.rect.midbottom,
                            hovered_obj.tile_type,
                            hovered_obj.flip_x,
                            self.create_bullet,
                        )
                        self.towers.add(new_tower)
                        self.visible_sprites.add(new_tower)

                        # remove destroyed tower
                        hovered_obj.kill()
                        hovered_obj = None  # No longer hovering

                # If it's a built tower (Tower)
                elif isinstance(hovered_obj, Tower):
                    if self.player.sprite.money >= hovered_obj.upgrade_cost:
                        if hovered_obj.level < hovered_obj.max_level:
                            self.player.sprite.money -= hovered_obj.upgrade_cost
                            hovered_obj.upgrade()

        self.mouse_pressed_prev = mouse_pressed
        return hovered_obj

    def draw_ui(self, hovered_obj=None):
        screen_w, screen_h = self.display_surface.get_size()

        money_text = f"${self.player.sprite.money}"
        money_surf = self.ui_font.render(money_text, True, (255, 215, 0))
        money_rect = money_surf.get_rect(topleft=(20, 0))

        money_shadow = self.ui_font.render(money_text, True, (0, 0, 0))
        money_shadow_rect = money_rect.copy()
        money_shadow_rect.x += 2
        money_shadow_rect.y += 2

        self.display_surface.blit(money_shadow, money_shadow_rect)
        self.display_surface.blit(money_surf, money_rect)

        wpn_cost = self.player.sprite.weapon_upgrade_cost
        wpn_level = self.player.sprite.weapon_level
        wpn_text = f"[E] upgrade weapon Lvl{wpn_level} (${wpn_cost})"
        wpn_surf = self.ui_font.render(wpn_text, True, (200, 200, 200))
        wpn_rect = wpn_surf.get_rect(topleft=(20, 50))
        wpn_shadow = self.ui_font.render(wpn_text, True, (0, 0, 0))
        wpn_sh_rect = wpn_rect.copy()
        wpn_sh_rect.x += 2
        wpn_sh_rect.y += 2
        self.display_surface.blit(wpn_shadow, wpn_sh_rect)
        self.display_surface.blit(wpn_surf, wpn_rect)

        reg_cost = self.player.sprite.regen_upgrade_cost
        reg_level = self.player.sprite.regen_level
        reg_text = f"[C] upgrade regeneration Lv{reg_level} (${reg_cost})"
        reg_surf = self.ui_font.render(reg_text, True, (200, 200, 200))
        reg_rect = reg_surf.get_rect(topleft=(20, 80))
        reg_shadow = self.ui_font.render(reg_text, True, (0, 0, 0))
        reg_sh_rect = reg_rect.copy()
        reg_sh_rect.x += 2
        reg_sh_rect.y += 2
        self.display_surface.blit(reg_shadow, reg_sh_rect)
        self.display_surface.blit(reg_surf, reg_rect)

        heal_cost = self.player.sprite.quick_heal_cost
        heal_text = f"[Q] full heal (${heal_cost})"
        heal_surf = self.ui_font.render(heal_text, True, (200, 200, 200))
        heal_rect = heal_surf.get_rect(topleft=(20, 110))
        heal_shadow = self.ui_font.render(heal_text, True, (0, 0, 0))
        heal_sh_rect = heal_rect.copy()
        heal_sh_rect.x += 2
        heal_sh_rect.y += 2
        self.display_surface.blit(heal_shadow, heal_sh_rect)
        self.display_surface.blit(heal_surf, heal_rect)

        # tooltip for buying/upgrading
        cost = 0
        text = ""
        if hovered_obj:
            mx, my = pygame.mouse.get_pos()

            if isinstance(hovered_obj, Tile):
                text = f"Repair: ${hovered_obj.price}"
                cost = hovered_obj.price
            elif isinstance(hovered_obj, Tower):
                if hovered_obj.level >= hovered_obj.max_level:
                    text = "Max Level"
                    cost = 0
                else:
                    text = (
                        f"Upgrade Lv{hovered_obj.level+1}: ${hovered_obj.upgrade_cost}"
                    )
                    cost = hovered_obj.upgrade_cost

            col = (0, 255, 0) if self.player.sprite.money >= cost else (255, 0, 0)

            tooltip_surf = self.ui_font.render(text, True, col)
            tooltip_rect = tooltip_surf.get_rect(topleft=(mx + 15, my))

            bg_rect = tooltip_rect.inflate(10, 10)
            pygame.draw.rect(self.display_surface, (0, 0, 0), bg_rect)
            pygame.draw.rect(self.display_surface, (255, 255, 255), bg_rect, 2)
            self.display_surface.blit(tooltip_surf, tooltip_rect)

        # morning celeb
        if self.show_celebration:
            self.celebration_timer -= 1
            if self.celebration_timer <= 0:
                self.show_celebration = False
            else:
                msg = f"day {self.day_count}"
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

    def run(self, is_menu=False):
        if not is_menu:
            self.day_night_cycle()
            self.spawn_night_enemies()

        self.visible_sprites.custom_draw(self.player.sprite, show_player=not is_menu)

        if self.current_darkness > 0:
            self.display_surface.blit(self.dark_overlay, (0, 0))

        self.rain.update()
        self.rain.draw()
        self.clouds.update(1.0, None, None)
        if is_menu:
            return

        hovered_tile = self.handle_interaction()

        self.draw_ui(hovered_tile)

        if self.check_game_over():
            return

        self.enemies.update(self.tiles, self.player.sprite)
        self.bullets.update(self.tiles)
        self.player.sprite.update(self.tiles, self.create_bullet)
        self.towers.update(self.enemies)

        # bullet collisions with enemies
        hits_bullets = pygame.sprite.groupcollide(
            self.enemies, self.bullets, False, True
        )
        if hits_bullets:
            for enemy, bullets in hits_bullets.items():
                for bullet in bullets:
                    if enemy.get_damage(bullet.damage):
                        # enemy killed!
                        reward = random.randint(10, 20)
                        self.player.sprite.money += reward

        # enemy collisions with player
        hits = pygame.sprite.spritecollide(self.player.sprite, self.enemies, False)
        if hits:
            for sprite in hits:
                self.player.sprite.get_damage(sprite.damage)
