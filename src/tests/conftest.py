# @generated "all" Gemini 2.0: Configuration for pytest with robust pygame mocks
import sys
import os
import pytest
from unittest.mock import MagicMock

current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_dir, ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)


class MockRect:
    """
    Simulates pygame.Rect. Stores coordinates as real numbers so calculations work.
    """

    def __init__(self, x=0, y=0, width=100, height=100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def left(self):
        return self.x

    @left.setter
    def left(self, val):
        self.x = val

    @property
    def right(self):
        return self.x + self.width

    @right.setter
    def right(self, val):
        self.x = val - self.width

    @property
    def top(self):
        return self.y

    @top.setter
    def top(self, val):
        self.y = val

    @property
    def bottom(self):
        return self.y + self.height

    @bottom.setter
    def bottom(self, val):
        self.y = val - self.height

    @property
    def centerx(self):
        return self.x + self.width // 2

    @centerx.setter
    def centerx(self, val):
        self.x = val - self.width // 2

    @property
    def centery(self):
        return self.y + self.height // 2

    @centery.setter
    def centery(self, val):
        self.y = val - self.height // 2

    @property
    def topleft(self):
        return (self.x, self.y)

    @property
    def midbottom(self):
        return (self.centerx, self.bottom)

    @midbottom.setter
    def midbottom(self, val):
        self.centerx, self.bottom = val

    def copy(self):
        return MockRect(self.x, self.y, self.width, self.height)

    def move(self, x, y):
        return MockRect(self.x + x, self.y + y, self.width, self.height)

    def inflate(self, w, h):
        return MockRect(
            self.x - w // 2, self.y - h // 2, self.width + w, self.height + h
        )

    def clamp(self, other):
        return self  # Simplified

    def colliderect(self, other):
        # Simplified collision logic for tests
        return (
            self.x < other.x + other.width
            and self.x + self.width > other.x
            and self.y < other.y + other.height
            and self.y + self.height > other.y
        )

    def collidepoint(self, pos):
        px, py = pos
        return (
            self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height
        )


class MockSurface:
    """
    Simulates pygame.Surface. Returns tuples for size and handles subsurface.
    """

    def __init__(self, size=(100, 100), *args, **kwargs):
        self._width, self._height = size

    def get_size(self):
        return (self._width, self._height)

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_rect(self, **kwargs):
        x, y = 0, 0
        # Basic position handling
        if "topleft" in kwargs:
            x, y = kwargs["topleft"]
        elif "center" in kwargs:
            cx, cy = kwargs["center"]
            x = cx - self._width // 2
            y = cy - self._height // 2
        elif "midbottom" in kwargs:
            cx, bottom = kwargs["midbottom"]
            x = cx - self._width // 2
            y = bottom - self._height

        return MockRect(x, y, self._width, self._height)

    def get_bounding_rect(self):
        return MockRect(0, 0, self._width, self._height)

    def convert_alpha(self):
        return self

    def convert(self):
        return self

    def subsurface(self, rect):
        return self  # Return self to allow chaining

    def set_colorkey(self, color):
        pass

    def get_at(self, pos):
        return (0, 0, 0, 0)

    def set_alpha(self, a):
        pass

    def fill(self, color):
        pass

    def blit(self, source, dest, area=None, special_flags=0):
        pass


class MockSprite:
    """
    Simulates pygame.sprite.Sprite.
    """

    def __init__(self, *args, **kwargs):
        self.image = MockSurface()
        self.rect = MockRect()
        self._Sprite__g = {}

    def kill(self):
        pass

    def add(self, *groups):
        pass

    def update(self, *args, **kwargs):
        pass


class MockGroup(list):
    """
    Simulates pygame.sprite.Group (as a list).
    """

    def __init__(self, *sprites):
        super().__init__(sprites)

    def add(self, *sprites):
        for s in sprites:
            if s not in self:
                self.append(s)

    def empty(self):
        self.clear()

    def sprites(self):
        return list(self)

    def draw(self, surface):
        pass

    def update(self, *args, **kwargs):
        for s in self:
            if hasattr(s, "update"):
                s.update(*args, **kwargs)

    def custom_draw(self, player, show_player=True):
        pass


# --- 3. Mocking Modules ---

# Create the mock pygame module
mock_pygame = MagicMock()

# Replace classes with our Dummy implementations
mock_pygame.sprite.Sprite = MockSprite
mock_pygame.sprite.Group = MockGroup
mock_pygame.sprite.GroupSingle = MockGroup
mock_pygame.Rect = MockRect
mock_pygame.Surface = MockSurface

# Mock Image loading to return our MockSurface
def mock_load(path):
    return MockSurface((100, 100))


mock_pygame.image.load.side_effect = mock_load
mock_pygame.transform.scale.return_value = MockSurface((100, 100))
mock_pygame.transform.flip.return_value = MockSurface((100, 100))

# Mock Font
mock_font = MagicMock()
mock_font.render.return_value = MockSurface((50, 20))  # Text returns a surface
mock_pygame.font.Font.return_value = mock_font

# Mock Display
mock_pygame.display.get_surface.return_value = MockSurface((1920, 1080))
mock_pygame.display.set_mode.return_value = MockSurface((1920, 1080))

# Time and Math
mock_pygame.time.get_ticks.return_value = 1000
mock_pygame.math.Vector2 = lambda x=0, y=0: MagicMock(x=x, y=y)

# Constants
mock_pygame.FULLSCREEN = 1
mock_pygame.SCALED = 2
mock_pygame.SRCALPHA = 32
mock_pygame.K_e = 101
mock_pygame.K_c = 99
mock_pygame.K_q = 113
mock_pygame.K_d = 100
mock_pygame.K_a = 97
mock_pygame.K_r = 114
mock_pygame.K_SPACE = 32
mock_pygame.K_LSHIFT = 304
mock_pygame.K_RSHIFT = 303
mock_pygame.K_ESCAPE = 27
mock_pygame.K_DOWN = 274
mock_pygame.K_UP = 273
mock_pygame.QUIT = 12
mock_pygame.KEYDOWN = 2

# Inject into sys.modules
sys.modules["pygame"] = mock_pygame

# Mock particlepy (external lib)
mock_particlepy = MagicMock()
sys.modules["particlepy"] = mock_particlepy
sys.modules["particlepy.particle"] = mock_particlepy.particle
sys.modules["particlepy.shape"] = mock_particlepy.shape

# --- 4. Fixtures ---


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """
    Mocks OS file operations.
    """
    # 1. Mock listdir to return dummy .png files so loops execute
    monkeypatch.setattr("os.listdir", lambda x: ["test.png"])

    # 2. Mock path.exists to always be true
    monkeypatch.setattr("os.path.exists", lambda x: True)

    # 3. Mock open() for high score reading/writing
    from unittest.mock import mock_open

    monkeypatch.setattr("builtins.open", mock_open(read_data="100"))
