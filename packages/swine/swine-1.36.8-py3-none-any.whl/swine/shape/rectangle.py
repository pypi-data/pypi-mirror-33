#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""""

from swine import GameObject, Scene
from .polygon import Polygon


class Rectangle(Polygon):
    def __init__(self, scene, width, height, fill=True, x=0, y=0, layer=0, colours=[]):
        # type: (Scene, int, int, bool, int, int, int, list[str]) -> None
        GameObject.__init__(self, scene=scene)
        x += (scene.window.width / 2) - (width / 2)
        y += (scene.window.height / 2) - (height / 2)

        points = [x, y,  # Bottom left
                  x + width, y,  # Bottom right
                  x + width, y + height,  # Top right
                  x, y + height]  # Top left
        Polygon.__init__(self, scene, fill, 4, x, y, layer, points, colours=colours)
