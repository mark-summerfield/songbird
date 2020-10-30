#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtWidgets import QFormLayout, QMessageBox, QSpinBox, QWidget

from Const import UNCHANGED
from Sql import Pragmas


class Mixin:

    def refresh_pragmas(self):
        widget = self.pragmasDock.widget()
        if widget is not None:
            widget.refresh()


class View(QWidget):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.pragmas = Pragmas(user_version=UNCHANGED)
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
        self.userVersionSpinbox.valueChanged.connect(self.on_user_version)


    def on_user_version(self):
        self.pragmas.user_version = self.userVersionSpinbox.value()
        self.dirty = True


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
        saved = not self.dirty
        errors = False
        if self.dirty and bool(self.model):
            errors = self.model.save_pragmas(self.pragmas)
            if errors:
                if not closing:
                    error = '\n'.join(errors)
                    QMessageBox.warning(
                        self, f'Pragma error — {qApp.applicationName()}',
                        f'Failed to save pragmas:\n{error}')
            else:
                saved = True
        self.dirty = not errors
        return saved
