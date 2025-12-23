# @generated "partially" Gemini: Added docstrings and type annotations
import pygame
from typing import Optional, List, Tuple


class Menu:
    """
    Handles the game menu states, rendering, and input.
    """

    def __init__(self, surface: pygame.Surface, font_path: str) -> None:
        self.display_surface = surface
        self.font = pygame.font.Font(font_path, 60)
        self.small_font = pygame.font.Font(font_path, 30)
        self.state = "MAIN"
        self.volume = 0.5
        self.mouse_pressed_prev = False
        self.current_score = 0
        self.best_score = 0

        self.buttons = {
            "MAIN": [
                ("PLAY", "PLAY_GAME"),
                ("CONTROLS", "CONTROLS"),
                ("SOUND", "SOUND"),
                ("CREDITS", "CREDITS"),
                ("QUIT", "QUIT_GAME"),
            ],
            "CREDITS": [("BACK", "MAIN")],
            "CONTROLS": [("BACK", "MAIN")],
            "SOUND": [("BACK", "MAIN")],
        }

    def draw(self) -> None:
        """Renders the current menu state."""
        overlay = pygame.Surface(self.display_surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.display_surface.blit(overlay, (0, 0))

        if self.state == "MAIN":
            score_text = (
                f"Current Score: {self.current_score}   Best Score: {self.best_score}"
            )
            self.draw_text(score_text, 100, self.small_font, color="Yellow")
            self.draw_buttons(self.buttons["MAIN"])
        elif self.state == "CREDITS":
            self.draw_text("CREDITS", 100)
            self.draw_text("programming: asilukas", 250, self.small_font)
            self.draw_text("music: schmauz", 300, self.small_font)
            self.draw_text("art: asilukas, szadiart ", 350, self.small_font)
            self.draw_buttons(self.buttons["CREDITS"])
        elif self.state == "CONTROLS":
            self.draw_text("CONTROLS", 100)
            self.draw_text(
                "A/D - move | SHIFT - sprint | SPACE - jump", 250, self.small_font
            )
            self.draw_text("Mouse Click - shoot", 320, self.small_font)
            self.draw_text("E - upgrade gun | C - upgrade regen", 390, self.small_font)
            self.draw_buttons(self.buttons["CONTROLS"])
        elif self.state == "SOUND":
            self.draw_text("SOUND SETTINGS", 100)
            vol_text = f"volume: {int(self.volume * 100)}"
            self.draw_text(vol_text, 250, self.small_font)
            self.draw_text("use Up/Down arrows", 320, self.small_font)
            self.draw_buttons(self.buttons["SOUND"])

    def draw_text(
        self,
        text: str,
        y: int,
        font: Optional[pygame.font.Font] = None,
        color: str = "White",
    ) -> None:
        """Helper to draw centered text."""
        if not font:
            font = self.font
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(self.display_surface.get_width() // 2, y))
        self.display_surface.blit(surf, rect)

    def draw_buttons(self, button_list: List[Tuple[str, str]]) -> None:
        """Helper to draw a list of buttons."""
        mx, my = pygame.mouse.get_pos()
        start_y = 450
        for i, (text, _) in enumerate(button_list):
            rect = pygame.Rect(
                self.display_surface.get_width() // 2 - 150,
                start_y + i * 80 - 30,
                300,
                60,
            )
            color = "yellow" if rect.collidepoint(mx, my) else "white"
            surf = self.small_font.render(text, True, color)
            self.display_surface.blit(surf, surf.get_rect(center=rect.center))

    def update_resume_state(self, is_resumable: bool) -> None:
        """Updates the main menu button text based on game state."""
        action = "PLAY_GAME"
        text = "RESUME" if is_resumable else "PLAY"
        self.buttons["MAIN"][0] = (text, action)

    def handle_input(self) -> Optional[str]:
        """Handles menu navigation and returns action triggers (PLAY/QUIT)."""
        keys = pygame.key.get_pressed()
        if self.state == "SOUND":
            if keys[pygame.K_DOWN]:
                self.volume = max(0.0, self.volume - 0.01)
                pygame.mixer.music.set_volume(self.volume)
            if keys[pygame.K_UP]:
                self.volume = min(1.0, self.volume + 0.01)
                pygame.mixer.music.set_volume(self.volume)

        mouse_pressed = pygame.mouse.get_pressed()[0]
        action_trigger = None

        if mouse_pressed and not self.mouse_pressed_prev:
            mx, my = pygame.mouse.get_pos()
            start_y = 450
            for i, (_, action) in enumerate(self.buttons[self.state]):
                rect = pygame.Rect(
                    self.display_surface.get_width() // 2 - 150,
                    start_y + i * 80 - 30,
                    300,
                    60,
                )
                if rect.collidepoint(mx, my):
                    if action == "PLAY_GAME":
                        action_trigger = "PLAY"
                    elif action == "QUIT_GAME":
                        action_trigger = "QUIT"
                    else:
                        self.state = action
                    break

        self.mouse_pressed_prev = mouse_pressed
        return action_trigger
