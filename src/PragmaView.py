#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtWidgets import QWidget


class Mixin:

    def refresh_pragmas(self):
        widget = self.pragmasDock.widget()
        if widget is not None:
            widget.refresh()


class View(QWidget):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.dirty = False


    def refresh(self):
        self.clear()
        if bool(self.model):
            pass # TODO
        print('PragmaView View.refresh')


    def clear(self):
        # TODO clear all widgets
        self.dirty = False


    def save(self, *, closing=False):
        # TODO what happens if there's an error and it can't save? We could
        # be closing down
        print(f'PragmaView View.save dirty={self.dirty} closing={closing}')
        if self.dirty and bool(self.model):
            pass # TODO
        self.dirty = False
