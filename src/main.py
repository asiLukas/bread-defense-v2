import os
import pygame
from level import Level

def load_level_map(filename):
    map_data = []
    try:
        with open(filename, 'r') as file:
            for line in file.readlines():
                map_data.append(line.strip())
    except FileNotFoundError:
        print(f"Error: Could not find {filename}")
        return []
    return map_data

def load_bg(filename, transparency=False):
    path = os.path.join("assets", "background", filename)
    if transparency:
        img = pygame.image.load(path).convert_alpha()
    else:
        img = pygame.image.load(path).convert()
    return pygame.transform.scale(img, (bg_w, bg_h))

def draw_bg(surface, img, x_pos, y_pos):
    relative_x = x_pos % bg_w
    
    surface.blit(img, (relative_x - bg_w, y_pos))
    
    if relative_x < screen_w:
        surface.blit(img, (relative_x, y_pos))

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_w, screen_h = screen.get_size()

pygame.display.set_caption("BDV2")
clock = pygame.time.Clock()

zoom_factor = 1.5 
bg_w = int(screen_w * zoom_factor)
bg_h = int(screen_h * zoom_factor)

bg_1 = load_bg("background1.png", transparency=False) 
bg_2 = load_bg("background4a.png", transparency=True)  
bg_3 = load_bg("background4b.png", transparency=True)  
bg_4 = load_bg("background3.png", transparency=True)  

level_data = load_level_map(os.path.join("assets", "map"))
level = Level(level_data, screen)

music_path = os.path.join("assets", "sound", "main_music.wav")
pygame.mixer.music.load(music_path)
pygame.mixer.music.set_volume(0.5) 
pygame.mixer.music.play(-1)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

    camera_x = level.visible_sprites.offset.x
    camera_y = level.visible_sprites.offset.y
    
    speed_1 = 0.05
    speed_2 = 0.09
    speed_3 = 0.11
    speed_4 = 0.15

    bg_1_x = -(camera_x * speed_1)
    bg_1_y = (screen_h - bg_h) // 2 - (camera_y * speed_1)
    bg_2_x = -(camera_x * speed_2)
    bg_2_y = (screen_h - bg_h) // 2 - (camera_y * speed_2)
    bg_3_x = -(camera_x * speed_3)
    bg_3_y = (screen_h - bg_h) // 2 - (camera_y * speed_3)
    bg_4_x = -(camera_x * speed_4)
    bg_4_y = (screen_h - bg_h) // 2 - (camera_y * speed_4)

    draw_bg(screen, bg_1, bg_1_x, bg_1_y)
    draw_bg(screen, bg_2, bg_2_x, bg_2_y)
    draw_bg(screen, bg_3, bg_3_x, bg_3_y)
    draw_bg(screen, bg_4, bg_4_x, bg_4_y)

    level.run()

    pygame.display.flip()
    clock.tick(60)
