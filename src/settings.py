# @generated "partially" Gemini: Added docstrings and type annotations
"""
Global settings and constants for the game.
"""

GAME_HEIGHT: int = 1080
TILE_SIZE: int = 128
MAP_WIDTH: int = 150
BORDER_LEFT_INDEX: int = 10
BORDER_RIGHT_INDEX: int = 140

# Day/Night cycle settings
DAY_CYCLE_LENGTH: int = (
    4000  # Total frames for a full day (at 60FPS, 3000 is 50 seconds)
)
NIGHT_START_THRESHOLD: float = 0.3  # Cycle point (0.0 to 1.0) where dusk begins
NIGHT_END_THRESHOLD: float = 0.95  # Cycle point where dawn begins
MAX_DARKNESS: int = 130  # Alpha value (0-255). Higher is darker.
CELEBRATION_DURATION: int = 250
