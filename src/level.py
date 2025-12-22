import pygame

from tile import Tile
from player import Player
from enemy import Enemy
from settings import TILE_SIZE


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_width() // 2
        self.half_h = self.display_surface.get_height() // 2

        self.camera_speed = 0.07 

        
    def custom_draw(self, player):
        target_x = player.rect.centerx - self.half_w
        target_y = player.rect.centery - self.half_h - 300

        self.offset.x += (target_x - self.offset.x) * self.camera_speed
        self.offset.y += (target_y - self.offset.y) * self.camera_speed

        sorted_sprites = sorted(self.sprites(), key=lambda sprite: sprite.z)

        for sprite in sorted_sprites:
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)


class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        
        self.visible_sprites = CameraGroup()
        
        self.tiles = pygame.sprite.Group() 
        self.enemies = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()

        self.setup_level(level_data)
        
    def setup_level(self, layout):
        enemy_map = {
            'e01': 'enemy01', 'e02': 'enemy02', 'e03': 'enemy03',
            'e04': 'enemy04', 'e05': 'enemy05', 'e06': 'enemy06',
        }

        for row_index, row in enumerate(layout):
            row_values = row.split(',')
            for col_index, val in enumerate(row_values):
                val = val.strip()
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                
                if val in ['0']:
                    continue 

                elif val == '99':
                    tile = Tile((x,y), TILE_SIZE, val)
                    self.tiles.add(tile)
                    self.visible_sprites.add(tile)
                
                elif val in [f'{i}' for i in range(1, 9)]:
                    tile = Tile((x,y), TILE_SIZE, val)
                    self.tiles.add(tile)
                    self.visible_sprites.add(tile)
                
                elif val in enemy_map:
                    enemy_variant = enemy_map[val]
                    enemy = Enemy(x, y, enemy_variant, 4)
                    self.enemies.add(enemy)
                    self.visible_sprites.add(enemy)
        
        p = Player(5000, 1000, 1)
        self.player.add(p)
        self.visible_sprites.add(p)

    def run(self):
        self.enemies.update(self.tiles)
        self.player.sprite.update(self.tiles) 

        self.visible_sprites.custom_draw(self.player.sprite)
