#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""""

import math

from swine import GameObject, Scene
from .polygon import Polygon


class Ellipse(Polygon):
    def __init__(self, scene, width, height, segments=3, fill=True, x=0, y=0, layer=0, colours=[]):
        # type: (Scene, int, int, int, bool, int, int, int, list[str]) -> None
        GameObject.__init__(self, scene=scene)
        points = []
        x += scene.window.width / 2
        y += scene.window.height / 2

        for i in range(segments):
            angle = math.radians(float(i) / segments * 360)

            _x = width * math.cos(angle) + x
            _y = height * math.sin(angle) + y

            points.append(_x)
            points.append(_y)

        Polygon.__init__(self, scene, fill, segments, x, y, layer, points, colours=colours)
