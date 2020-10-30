#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtWidgets import QFormLayout, QSpinBox, QWidget


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
        self.make_widgets()
        self.make_layout()
        self.make_connections()


    def make_widgets(self):
        self.userVersionSpinbox = QSpinBox()
        self.userVersionSpinbox.setRange(0, (2**31) - 1)


    def make_layout(self):
        form = QFormLayout()
        form.addRow('User Version', self.userVersionSpinbox)
        self.setLayout(form)


    def make_connections(self):
        pass # TODO


    def refresh(self):
        self.clear()
        if bool(self.model):
            pragmas = self.model.pragmas()
            self.userVersionSpinbox.setValue(pragmas.user_version)


    def clear(self):
        self.userVersionSpinbox.setValue(0)
        # TODO clear all widgets
        self.dirty = False


    def save(self, *, closing=False):
        # TODO what happens if there's an error and it can't save? We could
        # be closing down
        saved = False
        if self.dirty and bool(self.model):
            pass # TODO
            saved = True
        self.dirty = False
        return saved
