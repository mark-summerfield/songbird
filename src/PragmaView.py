#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import os
import pathlib

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QFormLayout, QLabel, QMessageBox, QSpinBox, QWidget)

from Const import MAX_I32
from Sql import Pragmas
from Ui import BlockSignals


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
        self.userVersionSpinbox.setRange(0, MAX_I32)
        # TODO make all widgets
        self.pathLabel = QLabel()
        self.pathLabel.setTextFormat(Qt.RichText)


    def make_layout(self):
        form = QFormLayout()
        form.addRow('User Version', self.userVersionSpinbox)
        # TODO add all widgets
        form.addRow(self.pathLabel)
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
            with BlockSignals(self):
                self.userVersionSpinbox.setValue(pragmas.user_version)
                # TODO refresh all widgets
                path = str(pathlib.Path(self.model.filename).parent)
                if not path.endswith(('/', '\\')):
                    path += os.sep
                self.pathLabel.setText(_PATH_TEMPLATE.format(path=path))
        self.dirty = False


    def clear(self):
        with BlockSignals(self):
            self.userVersionSpinbox.setValue(0)
            # TODO clear all widgets
            self.pathLabel.clear()
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


_PATH_TEMPLATE = 'Path <font color=navy>{path}</font>'
