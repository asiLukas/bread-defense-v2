# @generated "all" Gemini 2.0: utils tests
import utils
import settings


def test_generate_row_structure():
    row = utils.generate_row("sky")
    assert isinstance(row, str)
    tiles = row.split(",")
    assert len(tiles) == settings.MAP_WIDTH


def test_load_high_score_mocked(monkeypatch):
    from unittest.mock import mock_open

    m = mock_open(read_data="500")
    monkeypatch.setattr("builtins.open", m)

    score = utils.load_high_score()
    assert score == 500
