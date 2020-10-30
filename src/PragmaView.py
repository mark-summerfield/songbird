#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtWidgets import QFormLayout, QMessageBox, QSpinBox, QWidget

from Sql import Pragmas


class Mixin:

    def refresh_pragmas(self):
        self.pragmasDock.widget().refresh()


class View(QWidget):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.pragmas = Pragmas.unchanged()
        self.dirty = False
        self.make_widgets()
        self.make_layout()
        self.make_connections()


    def make_widgets(self):
        self.userVersionSpinbox = QSpinBox()
        self.userVersionSpinbox.setRange(0, (2**31) - 1)
        # TODO make all widgets


    def make_layout(self):
        form = QFormLayout()
        form.addRow('User Version', self.userVersionSpinbox)
        # TODO add all widgets
        self.setLayout(form)


    def make_connections(self):
        self.userVersionSpinbox.valueChanged.connect(self.on_user_version)
        # TODO connect all widgets


    def on_user_version(self):
        self.pragmas.user_version = self.userVersionSpinbox.value()
        self.dirty = True


    def refresh(self):
        self.clear()
        if bool(self.model):
            pragmas = self.model.pragmas()
            blocked = self.blockSignals(True)
            try:
                self.userVersionSpinbox.setValue(pragmas.user_version)
                # TODO refresh all widgets
            finally:
                self.blockSignals(blocked)
        self.dirty = False


    def clear(self):
        blocked = self.blockSignals(True)
        try:
            self.userVersionSpinbox.setValue(0)
            # TODO clear all widgets
        finally:
            self.blockSignals(blocked)
        self.dirty = False


    def save(self, *, closing=False):
        saved = False
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
                self.dirty = False
        return saved
