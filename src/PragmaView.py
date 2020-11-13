#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import os
import pathlib

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QFormLayout, QGroupBox, QLabel, QMessageBox, QSpinBox,
    QVBoxLayout, QWidget)

import Config
from Const import APPNAME, MAX_I32
from Sql import Pragmas
from Ui import BlockSignals


class Mixin:

    def refresh_pragmas(self):
        self.pragmasDock.widget().refresh()


class View(QWidget):

    def __init__(self, db):
        super().__init__()
        self.db = db
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
        self.configLabel = QLabel(Config.filename())


    def make_layout(self):
        form = QFormLayout()
        form.addRow('User Version', self.userVersionSpinbox)
        # TODO add all widgets
        self._add_grouped(form, 'Database Path', self.pathLabel)
        self._add_grouped(form, 'Configuration File', self.configLabel)
        self.setLayout(form)


    def _add_grouped(self, form, title, widget):
        box = QGroupBox(title)
        vbox = QVBoxLayout()
        vbox.addWidget(widget)
        box.setLayout(vbox)
        form.addRow(box)


    def make_connections(self):
        self.userVersionSpinbox.valueChanged.connect(self.on_user_version)
        # TODO connect all widgets (excl. configLabel)


    def on_user_version(self):
        self.pragmas.user_version = self.userVersionSpinbox.value()
        self.dirty = True


    def refresh(self):
        self.clear()
        if bool(self.db):
            pragmas = self.db.pragmas()
            with BlockSignals(self):
                self.userVersionSpinbox.setValue(pragmas.user_version)
                # TODO refresh all widgets (excl. configLabel)
                path = str(pathlib.Path(self.db.filename).parent)
                if not path.endswith(('/', '\\')):
                    path += os.sep
                self.pathLabel.setText(path)
        self.dirty = False


    def clear(self):
        with BlockSignals(self):
            self.userVersionSpinbox.setValue(0)
            # TODO clear all widgets (excl. configLabel)
            self.pathLabel.clear()
        self.dirty = False


    def save(self, *, closing=False):
        saved = False
        errors = False
        if self.dirty and bool(self.db):
            if errors := self.db.pragmas_save(self.pragmas):
                if not closing:
                    error = '\n'.join(errors)
                    QMessageBox.warning(self, f'Pragma error — {APPNAME}',
                                        f'Failed to save pragmas:\n{error}')
            else:
                saved = True
                self.dirty = False
        return saved
