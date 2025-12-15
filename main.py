import pygame

from player import Player

pygame.init()
screen = pygame.display.set_mode((1280, 720))
FPS = 60
clock = pygame.time.Clock()

player_group = pygame.sprite.GroupSingle()
player = Player(640, 360, scale_factor=4)
player_group.add(player)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    screen.fill("black")

    player_group.update()
    player_group.draw(screen)
    
    # debug collision
    # pygame.draw.rect(screen, "red", player.rect, 2)

    pygame.display.flip()
    clock.tick(FPS)
