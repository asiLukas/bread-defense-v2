import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, scale_factor=None):
        super().__init__()
        self.z = 2
        self.import_character_assets(scale_factor)
        
        # movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 5
        self.gravity = 0.8
        self.jump_speed = -16
        
        # states
        self.status = 'idle'
        self.facing_right = True
        
        # animation
        self.frame_index = 0
        self.animation_speed = 0
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(midbottom= (pos_x, pos_y))
         
        self.last_update_time = pygame.time.get_ticks()

    def import_character_assets(self, scale):
        self.animations = {'idle': [], 'run': []}

        for animation in self.animations.keys():
            full_path = os.path.join('assets', 'player', animation)
            self.animations[animation] = []
            
            try:
                files = sorted([f for f in os.listdir(full_path) if f.endswith('.png')])
                
                for file in files:
                    img_path = os.path.join(full_path, file)
                    image = pygame.image.load(img_path).convert_alpha()

                    corner_color = image.get_at((0, 0))
                    image.set_colorkey(corner_color)

                    rect = image.get_bounding_rect()
                    rect = rect.inflate(2, 2).clamp(image.get_rect())
                    image = image.subsurface(rect)
                    
                    # optional scale
                    w, h = image.get_size()
                    if not scale:
                        scale = 1
                    image = pygame.transform.scale(image, (int(w * scale), int(h * scale)))
                    
                    self.animations[animation].append(image)
            except FileNotFoundError:
                print(f"Error: Folder not found at {full_path}")

    def get_input(self):
        keys = pygame.key.get_pressed()

        # movement
        if keys[pygame.K_d]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.facing_right = False
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE] and self.direction.y == 0: # only jump if on ground
            self.jump()

    def jump(self):
        self.direction.y = self.jump_speed

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def check_horizontal_collisions(self, tiles):
        self.rect.x += self.direction.x * self.speed
        
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                if self.direction.x > 0: # right
                    self.rect.right = tile.rect.left
                elif self.direction.x < 0: # left
                    self.rect.left = tile.rect.right

    def check_vertical_collisions(self, tiles):
        self.apply_gravity()
        
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                if self.direction.y > 0: # falling
                    self.rect.bottom = tile.rect.top
                    self.direction.y = 0 # stop falling
                elif self.direction.y < 0: # jumping into ceiling
                    self.rect.top = tile.rect.bottom
                    self.direction.y = 0

    def get_status(self):
        if self.direction.x != 0:
            # when switching from idle to run, make sure we reset index
            if self.status != 'run':
                self.frame_index = 0
            self.status = 'run'
        else:
            self.status = 'idle'

    def animate(self):
        animation = self.animations[self.status]
        current_time = pygame.time.get_ticks()
        
        if self.status == 'idle':
            if self.frame_index in (6, 7, 8, 9, 10):
                # blinking
                frame_duration = 100
            else:
                # breathing
                frame_duration = 500
        else:
            # running
            frame_duration = 100

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

        # adjust rect based on animation
        previous_feet_position = self.rect.midbottom  
        self.rect = self.image.get_rect()             
        self.rect.midbottom = previous_feet_position  
            
    def update(self, tiles):
        self.get_input()
        self.get_status()
        self.check_horizontal_collisions(tiles)
        self.check_vertical_collisions(tiles)
        self.animate()
