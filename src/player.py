import pygame
import os


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, scale_factor=None):
        super().__init__()
        self.z = 2
        self.import_character_assets(scale_factor)

        # Load bullet assets
        self.bullet_surf = pygame.image.load(
            os.path.join("assets", "bullet.png")
        ).convert_alpha()
        self.shoot_sound = pygame.mixer.Sound(
            os.path.join("assets", "sound", "bullet_sound.wav")
        )
        self.shoot_sound.set_volume(0.4)

        self.hit_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "hit.wav"))
        self.hit_sound.set_volume(0.5)

        # movement
        self.direction = pygame.math.Vector2(0, 0)
        self.walk_speed = 6
        self.sprint_speed = 11
        self.speed = self.walk_speed
        self.gravity = 0.8
        self.jump_speed = -16

        # sprint & Stamina
        self.is_sprinting = False
        self.max_stamina = 300
        self.current_stamina = self.max_stamina

        # health
        self.max_health = 100
        self.current_health = self.max_health
        self.invincible = True
        self.invincibility_duration = 1000  # 1 second of immunity after hit
        self.hit_time = 0
        self.is_dead = False

        self.money = 30

        # upgrades
        self.damage = 20
        self.weapon_level = 1
        self.weapon_upgrade_cost = 200
        self.regen_level = 0
        self.regen_upgrade_cost = 150
        self.last_regen_time = 0
        self.quick_heal_cost = 70

        # Shooting
        self.shoot_cooldown = 400
        self.last_shoot_time = 0

        # double tap logic
        self.last_tap_time = 0
        self.last_tap_key = None
        self.double_tap_threshold = 250
        self.previous_keys = pygame.key.get_pressed()

        # states
        self.status = "idle"
        self.facing_right = True

        # animation
        self.frame_index = 0
        self.animation_speed = 0
        self.image = self.animations["idle"][self.frame_index]
        self.rect = self.image.get_rect(midbottom=(pos_x, pos_y))

        self.last_update_time = pygame.time.get_ticks()

    def import_character_assets(self, scale):
        self.animations = {"idle": [], "run": []}

        for animation in self.animations.keys():
            full_path = os.path.join("assets", "player", animation)
            self.animations[animation] = []

            try:
                files = sorted([f for f in os.listdir(full_path) if f.endswith(".png")])

                for file in files:
                    img_path = os.path.join(full_path, file)
                    image = pygame.image.load(img_path).convert_alpha()

                    rect = image.get_bounding_rect()
                    rect = rect.inflate(2, 2).clamp(image.get_rect())
                    image = image.subsurface(rect)

                    # optional scale
                    w, h = image.get_size()
                    if not scale:
                        scale = 1
                    image = pygame.transform.scale(
                        image, (int(w * scale), int(h * scale))
                    )

                    self.animations[animation].append(image)
            except FileNotFoundError:
                print(f"Error: Folder not found at {full_path}")

    def get_input(self, create_bullet_callback):
        if self.is_dead:
            return
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()

        just_pressed_d = keys[pygame.K_d] and not self.previous_keys[pygame.K_d]
        just_pressed_a = keys[pygame.K_a] and not self.previous_keys[pygame.K_a]
        just_pressed_u = keys[pygame.K_u] and not self.previous_keys[pygame.K_u]
        just_pressed_h = keys[pygame.K_h] and not self.previous_keys[pygame.K_h]
        just_pressed_q = keys[pygame.K_q] and not self.previous_keys[pygame.K_q]

        if not keys[pygame.K_d] and not keys[pygame.K_a]:
            self.is_sprinting = False
            self.speed = self.walk_speed

        # Shooting input
        if keys[pygame.K_j]:
            if current_time - self.last_shoot_time >= self.shoot_cooldown:
                self.shoot_sound.play()
                direction = 1 if self.facing_right else -1
                # Offset bullet slightly to match player height
                bullet_y = self.rect.centery + 10
                create_bullet_callback(
                    self.rect.centerx,
                    bullet_y,
                    direction,
                    self.bullet_surf,
                    self.damage,
                )
                self.last_shoot_time = current_time

        # weapon upgrade
        if just_pressed_u:
            if self.money >= self.weapon_upgrade_cost:
                self.money -= self.weapon_upgrade_cost
                self.weapon_level += 1
                self.damage = int(self.damage * 1.5)
                self.weapon_upgrade_cost = int(self.weapon_upgrade_cost * 1.5)
        # health upgrade
        if just_pressed_h:
            if self.money >= self.regen_upgrade_cost:
                self.money -= self.regen_upgrade_cost
                self.regen_level += 1
                # Increase cost
                self.regen_upgrade_cost = int(self.regen_upgrade_cost * 1.5)

        # quick heal
        if just_pressed_q:
            if (
                self.money >= self.quick_heal_cost
                and self.current_health < self.max_health
            ):
                self.money -= self.quick_heal_cost
                self.current_health = self.max_health

        # double Tap Check
        if just_pressed_d:
            if self.last_tap_key == "d" and (
                current_time - self.last_tap_time < self.double_tap_threshold
            ):
                self.is_sprinting = True
                self.speed = self.sprint_speed
            self.last_tap_time = current_time
            self.last_tap_key = "d"

        if just_pressed_a:
            if self.last_tap_key == "a" and (
                current_time - self.last_tap_time < self.double_tap_threshold
            ):
                self.is_sprinting = True
                self.speed = self.sprint_speed
            self.last_tap_time = current_time
            self.last_tap_key = "a"

        if keys[pygame.K_d]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.facing_right = False
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE] and self.direction.y == 0:
            self.jump()

    def get_damage(self, amount):
        if not self.invincible and not self.is_dead:
            if self.hit_sound:
                self.hit_sound.play()
            self.current_health -= amount
            self.invincible = True
            self.hit_time = pygame.time.get_ticks()

            self.direction.y = -10  # Knockback

            if self.current_health <= 0:
                self.kill_player()  # Trigger Death

    def kill_player(self):
        self.current_health = 0
        self.is_dead = True
        self.direction.x = 0

    def manage_stamina(self):
        if self.is_sprinting:
            self.current_stamina -= 1.5
            if self.current_stamina <= 0:
                self.current_stamina = 0
                self.is_sprinting = False
                self.speed = self.walk_speed
        else:
            if self.current_stamina < self.max_stamina:
                self.current_stamina += 2

    def passive_regeneration(self):
        if self.regen_level > 0 and not self.is_dead:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_regen_time >= 1000:
                heal_amount = self.regen_level

                if self.current_health < self.max_health:
                    self.current_health += heal_amount
                    if self.current_health > self.max_health:
                        self.current_health = self.max_health

                self.last_regen_time = current_time

    def invincibility_timer(self):
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hit_time >= self.invincibility_duration:
                self.invincible = False
                self.image.set_alpha(255)

    def jump(self):
        self.direction.y = self.jump_speed

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def check_horizontal_collisions(self, tiles):
        self.rect.x += self.direction.x * self.speed

        for tile in tiles:
            # Check is_solid property (default to True if attribute missing)
            if getattr(tile, "is_solid", True):
                if tile.rect.colliderect(self.rect):
                    if self.direction.x > 0:  # right
                        self.rect.right = tile.rect.left
                    elif self.direction.x < 0:  # left
                        self.rect.left = tile.rect.right

    def check_vertical_collisions(self, tiles):
        self.apply_gravity()

        for tile in tiles:
            if getattr(tile, "is_solid", True):
                if tile.rect.colliderect(self.rect):
                    if self.direction.y > 0:  # falling
                        self.rect.bottom = tile.rect.top
                        self.direction.y = 0
                    elif self.direction.y < 0:  # ceiling
                        self.rect.top = tile.rect.bottom
                        self.direction.y = 0

    def get_status(self):
        if self.direction.x != 0:
            if self.status != "run":
                self.frame_index = 0
            self.status = "run"
        else:
            self.status = "idle"

    def animate(self):
        animation = self.animations[self.status]
        current_time = pygame.time.get_ticks()

        if self.status == "idle":
            if self.frame_index in (6, 7, 8, 9, 10):
                frame_duration = 100
            else:
                frame_duration = 500
        else:
            frame_duration = 60 if self.is_sprinting else 100

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

        if self.invincible:
            # flicker every 100ms
            alpha = 0 if (current_time // 100) % 2 == 0 else 255
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)
        previous_feet_position = self.rect.midbottom
        self.rect = self.image.get_rect()
        self.rect.midbottom = previous_feet_position

    def draw_bars(self, surface, offset_x, offset_y):
        if self.is_dead:
            return
        bar_width = 50
        bar_height = 6

        draw_x = self.rect.centerx - (bar_width // 2) - offset_x
        start_y = self.rect.top - 25 - offset_y

        # health bar
        health_ratio = self.current_health / self.max_health
        health_fill = int(bar_width * health_ratio)

        hp_bg_rect = pygame.Rect(draw_x, start_y, bar_width, bar_height)
        hp_fill_rect = pygame.Rect(draw_x, start_y, health_fill, bar_height)

        pygame.draw.rect(surface, (60, 0, 0), hp_bg_rect)
        pygame.draw.rect(surface, (200, 0, 0), hp_fill_rect)
        pygame.draw.rect(surface, (0, 0, 0), hp_bg_rect, 1)

        # stamina bar
        stamina_y = start_y + bar_height + 2
        stamina_ratio = self.current_stamina / self.max_stamina
        stamina_fill = int(bar_width * stamina_ratio)

        st_bg_rect = pygame.Rect(draw_x, stamina_y, bar_width, bar_height)
        st_fill_rect = pygame.Rect(draw_x, stamina_y, stamina_fill, bar_height)

        st_color = (200, 200, 0) if self.current_stamina < 20 else (0, 200, 0)

        pygame.draw.rect(surface, (60, 60, 60), st_bg_rect)
        pygame.draw.rect(surface, st_color, st_fill_rect)
        pygame.draw.rect(surface, (0, 0, 0), st_bg_rect, 1)

    def update(self, tiles, create_bullet_callback):
        self.get_input(create_bullet_callback)
        self.manage_stamina()
        self.passive_regeneration()
        self.invincibility_timer()
        self.get_status()
        self.check_horizontal_collisions(tiles)
        self.check_vertical_collisions(tiles)
        self.animate()

        self.previous_keys = pygame.key.get_pressed()
