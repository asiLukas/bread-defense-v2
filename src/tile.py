# @generated "partially" Gemini: Added docstrings and type annotations
import os
from typing import Tuple, Optional, Dict, Any

import pygame


class Tile(pygame.sprite.Sprite):
    """
    Represents a static object in the world (floor, decor, destroyed towers).
    """

    def __init__(
        self, pos: Tuple[int, int], size: int, tile_type: str, flip_x: bool = False
    ) -> None:
        super().__init__()
        self.z = 0
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft=pos)

        self.tile_type = tile_type
        self.flip_x = flip_x
        self.price = 0
        self.is_buyable = False
        self.is_solid = True

        self._setup_tile(pos, size)

    def _setup_tile(self, pos: Tuple[int, int], size: int) -> None:
        full_path = os.path.join("assets", "tiles")
        tower_path = os.path.join("assets", "towers")

        # Definition of tile properties for cleaner logic
        tile_defs: Dict[str, Dict[str, Any]] = {
            "1": {"file": "floor1.png", "dir": full_path},
            "2": {"file": "floor2.png", "dir": full_path},
            "3": {"file": "floor3.png", "dir": full_path},
            "4": {"file": "inn1.png", "dir": full_path},
            "5": {"file": "inn2.png", "dir": full_path},
            "6": {"file": "inn3.png", "dir": full_path},
            "7": {"file": "inn4.png", "dir": full_path},
            "101": {"file": "grass_cliff.png", "dir": full_path, "scale": 2},
            "102": {
                "file": "small_tree.png",
                "dir": full_path,
                "scale": 2,
                "anchor": "midtop",
            },
            "103": {
                "file": "bigger_tree.png",
                "dir": full_path,
                "scale": 2,
                "anchor": "midtop",
            },
            "104": {
                "file": "tree.png",
                "dir": full_path,
                "scale": 2,
                "anchor": "center",
            },
            "105": {
                "file": "big_tree.png",
                "dir": full_path,
                "scale": 2,
                "anchor": "center",
            },
            "106": {
                "file": "big_cliff.png",
                "dir": full_path,
                "scale": 2,
                "anchor": "center",
            },
            "107": {
                "file": "small_cliff.png",
                "dir": full_path,
                "scale": 2,
                "anchor": "center",
            },
            "200": {
                "file": "cannon_destroyed.png",
                "dir": tower_path,
                "price": 50,
                "buyable": True,
                "solid": False,
                "scale": 4,
                "anchor": "midbottom",
            },
            "201": {
                "file": "archer1_destroyed.png",
                "dir": tower_path,
                "price": 30,
                "buyable": True,
                "solid": False,
                "scale": 4,
                "anchor": "midbottom",
            },
            "202": {
                "file": "archer2_destroyed.png",
                "dir": tower_path,
                "price": 70,
                "buyable": True,
                "solid": False,
                "scale": 4,
                "anchor": "midbottom",
            },
        }

        if self.tile_type in tile_defs:
            data = tile_defs[self.tile_type]
            self.price = data.get("price", 0)
            self.is_buyable = data.get("buyable", False)
            self.is_solid = data.get("solid", True)

            img_path = os.path.join(data["dir"], data["file"])

            # Destroyed Towers are interactive/buyable
            if self.is_buyable or int(self.tile_type) > 100:
                self.image = pygame.image.load(img_path).convert_alpha()
            else:
                self.image = pygame.image.load(img_path).convert()

            scale = data.get("scale", 1)
            if scale != 1:
                w, h = self.image.get_size()
                self.image = pygame.transform.scale(
                    self.image, (int(w * scale), int(h * scale))
                )
            else:
                self.image = pygame.transform.scale(self.image, (size, size))

            if self.flip_x:
                self.image = pygame.transform.flip(self.image, True, False)

            anchor = data.get("anchor", "topleft")
            if anchor == "midtop":
                self.rect = self.image.get_rect(midtop=pos)
            elif anchor == "midbottom":
                self.rect = self.image.get_rect(midbottom=pos)
            elif anchor == "center":
                self.rect = self.image.get_rect(center=pos)
            else:
                self.rect = self.image.get_rect(topleft=pos)

        else:
            # Fallback for undefined tiles
            self.image.set_alpha(100)
            self.rect = self.image.get_rect(topleft=pos)
