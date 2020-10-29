#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtWidgets import QWidget


class Mixin:

    def refresh_pragmas(self):
        view = self.pragmasDock.widget()
        if view is not None:
            view.refresh()


class View(QWidget):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.dirty = False


    def refresh(self, model):
        self.clear()
        if bool(self.model):
            pass # TODO
        print('PragmaView View.refresh')


    def clear(self):
        # TODO clear all widgets
        self.dirty = False


    def save(self):
        if self.dirty and bool(self.model):
            pass # TODO
        print(f'PragmaView View.save {self.dirty}')
