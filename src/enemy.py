import pygame
import os

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, enemy_variant='enemy_01', scale_factor=None):
        super().__init__()
        self.z = 1
        self.import_assets(enemy_variant, scale_factor)
        
        # animation
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations['run'][self.frame_index]
        
        # movement
        self.direction = pygame.math.Vector2(1, 0)
        self.speed = 2
        self.gravity = 0.8
        self.facing_right = True
        
        self.rect = self.image.get_rect(midbottom=(pos_x, pos_y))
        
        self.hitbox = self.rect.inflate(-20, 0) 
        
        self.last_update_time = pygame.time.get_ticks()

    def import_assets(self, variant, scale):
        self.animations = {'run': []}
        full_path = os.path.join('assets', variant, 'run')
        try:
            files = sorted([f for f in os.listdir(full_path) if f.endswith('.png')])
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
                self.animations['run'].append(image)
        except FileNotFoundError:
            surf = pygame.Surface((32, 32))
            surf.fill('red')
            self.animations['run'].append(surf)

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.hitbox.y += self.direction.y

    def check_vertical_collisions(self, tiles):
        self.apply_gravity()
        for tile in tiles:
            if tile.rect.colliderect(self.hitbox):
                if self.direction.y > 0: 
                    self.hitbox.bottom = tile.rect.top
                    self.direction.y = 0

    def move_and_check_walls(self, tiles):
        self.hitbox.x += self.direction.x * self.speed
        
        for tile in tiles:
            if tile.rect.colliderect(self.hitbox):
                if self.direction.x > 0:
                    self.hitbox.right = tile.rect.left
                    self.direction.x = -1 
                    self.facing_right = False
                elif self.direction.x < 0:
                    self.hitbox.left = tile.rect.right
                    self.direction.x = 1 
                    self.facing_right = True

    def animate(self):
        animation = self.animations['run']
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_update_time > 100:
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

    def update(self, tiles):
        self.move_and_check_walls(tiles)
        self.check_vertical_collisions(tiles)
        self.animate()
