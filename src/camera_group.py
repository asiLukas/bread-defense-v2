import pygame


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.screen_w = self.display_surface.get_width()
        self.screen_h = self.display_surface.get_height()

        self.offset = pygame.math.Vector2()
        self.half_w = self.screen_w // 2
        self.half_h = self.screen_h // 2
        self.camera_speed = 0.07

    def custom_draw(self, player):
        target_x = player.rect.centerx - self.half_w
        target_y = player.rect.centery - self.half_h - 300

        self.offset.x += (target_x - self.offset.x) * self.camera_speed
        self.offset.y += (target_y - self.offset.y) * self.camera_speed

        # layered Draw
        layers = {0: [], 1: [], 2: [], 3: []}

        for sprite in self.sprites():
            # don't process off-screen sprites!
            offset_pos_x = sprite.rect.x - self.offset.x
            offset_pos_y = sprite.rect.y - self.offset.y

            if (
                -sprite.rect.width < offset_pos_x < self.screen_w
                and -sprite.rect.height < offset_pos_y < self.screen_h
            ):

                layers[sprite.z].append((sprite, (offset_pos_x, offset_pos_y)))

        for z in range(4):
            for sprite, pos in layers[z]:
                self.display_surface.blit(sprite.image, pos)
                if hasattr(sprite, "draw_bars"):
                    sprite.draw_bars(self.display_surface, self.offset.x, self.offset.y)
