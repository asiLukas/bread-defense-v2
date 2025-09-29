import pygame

pygame.init()

screen = pygame.display.set_mode((1280,720))
FPS = 60

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    screen.fill("purple")  

    pygame.display.flip()
    clock.tick(FPS)
