import pygame

import os

from level import Level
from menu import Menu
from settings import GAME_HEIGHT
from utils import tower_defense_map, load_bg, draw_bg

pygame.init()
monitor_info = pygame.display.Info()
monitor_w = monitor_info.current_w
monitor_h = monitor_info.current_h
monitor_ratio = monitor_w / monitor_h
flags = pygame.FULLSCREEN | pygame.SCALED
GAME_WIDTH = int(GAME_HEIGHT * monitor_ratio)
screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT), flags)
screen_w, screen_h = screen.get_size()

pygame.display.set_caption("BDV2")
clock = pygame.time.Clock()

zoom_factor = 1.5
bg_w = int(screen_w * zoom_factor)
bg_h = int(screen_h * zoom_factor)

bg_1 = load_bg("background1.png", (bg_w, bg_h), transparency=False)
bg_2 = load_bg("background4a.png", (bg_w, bg_h), transparency=True)
bg_3 = load_bg("background4b.png", (bg_w, bg_h), transparency=True)
bg_4 = load_bg("background3.png", (bg_w, bg_h), transparency=True)

level = Level(tower_defense_map, screen)
menu = Menu(screen, os.path.join("assets", "font.ttf"))
game_state = "MENU"

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
                game_state = "MENU"

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

    draw_bg(screen, bg_1, bg_1_x, bg_1_y, bg_w, screen_w)
    draw_bg(screen, bg_2, bg_2_x, bg_2_y, bg_w, screen_w)
    draw_bg(screen, bg_3, bg_3_x, bg_3_y, bg_w, screen_w)
    draw_bg(screen, bg_4, bg_4_x, bg_4_y, bg_w, screen_w)

    if game_state == "MENU":
        level.run(is_menu=True)
        action = menu.handle_input()
        if action == "PLAY":
            game_state = "PLAYING"
        elif action == "QUIT":
            pygame.quit()
            raise SystemExit
        menu.draw()
    else:
        level.run(is_menu=False)

    pygame.display.flip()
    clock.tick(60)
