#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

from kytten import Input as KInput

from .widget import Widget


class Input(Widget):
    def __init__(self, scene, text, command=None, length=10, limit=None, disabled=False, x=0, y=0):
        Widget.__init__(self, scene, KInput(text, length=length, max_length=limit, on_input=command, disabled=disabled), x, y)
