# @generated "all" Gemini 2.0: Unit tests for the world logic

from level import Level
from tile import Tile
from rain import Rain


def test_tile_properties():
    t1 = Tile((0, 0), 64, "1")
    assert t1.is_solid

    t_tower = Tile((0, 0), 64, "200")
    assert t_tower.is_buyable
    assert t_tower.price > 0
    assert not t_tower.is_solid


def test_level_setup():
    from conftest import MockSurface

    surf = MockSurface()
    level_data = ["0,1"]

    lvl = Level(level_data, surf)

    # Check that tiles were added
    assert len(lvl.tiles) > 0
    assert lvl.day_count == 1


def test_day_night_cycle():
    from conftest import MockSurface

    surf = MockSurface()
    lvl = Level(["0"], surf)

    # Reset timer
    lvl.day_timer = 0
    lvl.day_night_cycle()
    assert not lvl.is_night

    # Import constant to set time to night
    from settings import DAY_CYCLE_LENGTH

    lvl.day_timer = int(DAY_CYCLE_LENGTH * 0.5)
    lvl.day_night_cycle()

    assert lvl.is_night


def test_rain_spawn():
    from conftest import MockSurface

    surf = MockSurface((800, 600))
    rain = Rain(surf)
    assert len(rain.drops) > 0
