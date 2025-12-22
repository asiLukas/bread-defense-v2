import pygame
import os


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, enemy_variant="enemy_01", scale_factor=None):
        super().__init__()
        self.z = 1
        self.import_assets(enemy_variant, scale_factor)

        # animation
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations["run"][self.frame_index]

        # movement
        self.direction = pygame.math.Vector2(1, 0)
        self.gravity = 0.8

        # AI stats
        self.walk_speed = 2
        self.chase_speed = 4
        self.jump_speed = -16
        self.speed = self.walk_speed
        self.sight_range = 400
        self.state = "patrol"

        self.facing_right = True
        self.on_ground = False

        self.rect = self.image.get_rect(midbottom=(pos_x, pos_y))
        self.hitbox = self.rect.inflate(-20, 0)

        self.last_update_time = pygame.time.get_ticks()

    def import_assets(self, variant, scale):
        self.animations = {"run": []}
        full_path = os.path.join("assets", variant, "run")
        try:
            files = sorted([f for f in os.listdir(full_path) if f.endswith(".png")])
            for file in files:
                img_path = os.path.join(full_path, file)
                image = pygame.image.load(img_path).convert_alpha()

                # force transparent
                corner_color = image.get_at((0, 0))
                image.set_colorkey(corner_color)

                rect = image.get_bounding_rect()
                image = image.subsurface(rect)

                w, h = image.get_size()
                if not scale:
                    scale = 1
                image = pygame.transform.scale(image, (int(w * scale), int(h * scale)))
                self.animations["run"].append(image)
        except FileNotFoundError:
            surf = pygame.Surface((32, 32))
            surf.fill("red")
            self.animations["run"].append(surf)

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.hitbox.y += self.direction.y

    def jump(self):
        if self.on_ground:
            self.direction.y = self.jump_speed
            self.on_ground = False

    def check_vertical_collisions(self, tiles):
        self.apply_gravity()

        # assume not on ground until proven otherwise
        self.on_ground = False

        for tile in tiles:
            if tile.rect.colliderect(self.hitbox):
                if self.direction.y > 0:
                    self.hitbox.bottom = tile.rect.top
                    self.direction.y = 0
                    self.on_ground = True
                elif self.direction.y < 0:
                    self.hitbox.top = tile.rect.bottom
                    self.direction.y = 0

    def check_ledge(self, tiles):
        if self.direction.y != 0:
            return True

        look_ahead_distance = 20
        if self.facing_right:
            look_x = self.hitbox.right + look_ahead_distance
        else:
            look_x = self.hitbox.left - look_ahead_distance

        look_y = self.hitbox.bottom + 10
        check_rect = pygame.Rect(look_x - 5, look_y - 10, 10, 20)

        for tile in tiles:
            if tile.rect.colliderect(check_rect):
                return True
        return False

    def get_player_data(self, player):
        enemy_center = self.rect.center
        player_center = player.rect.center

        dx = player_center[0] - enemy_center[0]
        dy = player_center[1] - enemy_center[1]
        dist = (dx**2 + dy**2) ** 0.5

        return dist, dx, dy

    def behavior(self, player):
        dist, dx, dy = self.get_player_data(player)

        if dist < self.sight_range:
            self.state = "chase"
        else:
            self.state = "patrol"

        if self.state == "chase":
            self.speed = self.chase_speed

            if dx > 0:
                self.direction.x = 1
                self.facing_right = True
            else:
                self.direction.x = -1
                self.facing_right = False

            if dy < -100 and self.on_ground:
                self.jump()

        else:
            self.speed = self.walk_speed

    def move_and_check_walls(self, tiles):
        self.hitbox.x += self.direction.x * self.speed

        for tile in tiles:
            if tile.rect.colliderect(self.hitbox):
                if self.direction.x > 0:
                    self.hitbox.right = tile.rect.left

                    # AI DECISION: jump or turn
                    if self.state == "chase" and self.on_ground:
                        self.jump()
                    else:
                        self.direction.x = -1
                        self.facing_right = False

                elif self.direction.x < 0:
                    self.hitbox.left = tile.rect.right

                    # AI DECISION: jump or turn
                    if self.state == "chase" and self.on_ground:
                        self.jump()
                    else:
                        self.direction.x = 1
                        self.facing_right = True

        if self.on_ground:
            is_safe = self.check_ledge(tiles)
            if not is_safe:
                if self.state == "patrol":
                    self.direction.x *= -1
                    self.facing_right = not self.facing_right

    def animate(self):
        animation = self.animations["run"]
        current_time = pygame.time.get_ticks()

        speed_modifier = 0.5 if self.state == "chase" else 1.0
        frame_duration = 100 * speed_modifier

        if current_time - self.last_update_time > frame_duration:
            self.frame_index += 1
            if self.frame_index >= len(animation):
                self.frame_index = 0
            self.last_update_time = current_time

        current_image = animation[self.frame_index]

        if not self.facing_right:
            self.image = pygame.transform.flip(current_image, True, False)
        else:
            self.image = current_image

        self.rect = self.image.get_rect()
        self.rect.midbottom = self.hitbox.midbottom

    def update(self, tiles, player):
        self.behavior(player)
        self.move_and_check_walls(tiles)
        self.check_vertical_collisions(tiles)
        self.animate()
