#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import contextlib
import pathlib

from PySide2.QtCore import QTimer
from PySide2.QtGui import QKeySequence, Qt
from PySide2.QtWidgets import QMenu

import Config
from Ui import make_action


class Mixin:

    def make_file_actions(self):
        path = Config.path()
        self.file_new_action = make_action(
            self, path / 'images/document-new.svg', '&New...',
            self.file_new, QKeySequence.New)
        self.file_open_action = make_action(
            self, path / 'images/document-open.svg', '&Open...',
            self.file_open, QKeySequence.Open)
        self.file_open_recent_action = make_action(
            self, path / 'images/document-open.svg', 'Open &Recent')
        self.file_open_recent_menu = QMenu(self)
        self.file_open_recent_action.setMenu(self.file_open_recent_menu)
        self.file_save_action = make_action(
            self, path / 'images/filesave.svg', '&Save', self.file_save,
            QKeySequence.Save)
        self.file_saveas_action = make_action(
            self, path / 'images/filesaveas.svg', 'Save &As...',
            self.file_saveas, QKeySequence.SaveAs)
        self.file_backup_action = make_action(
            self, path / 'images/filesaveas.svg', '&Backup...',
            self.file_backup)
        self.file_import_action = make_action(
            self, path / 'images/import.svg', '&Import...',
            self.file_import)
        self.file_export_action = make_action(
            self, path / 'images/export.svg', '&Export...',
            self.file_export)
        self.file_quit_action = make_action(
            self, path / 'images/shutdown.svg', '&Quit', self.close,
            QKeySequence(Qt.CTRL + Qt.Key_Q))


    @property
    def file_actions_for_menu(self):
        return (self.file_new_action, self.file_open_action,
                self.file_open_recent_action, self.file_save_action,
                self.file_saveas_action, self.file_backup_action, None,
                self.file_import_action, self.file_export_action, None,
                self.file_quit_action)

    @property
    def file_actions_for_toolbar(self):
        return (self.file_new_action, self.file_open_action,
                self.file_save_action, None, self.file_import_action,
                self.file_export_action)


    def file_update_ui(self):
        enable = bool(self.model)
        for action in (self.file_save_action, self.file_saveas_action,
                       self.file_backup_action, self.file_export_action):
            action.setEnabled(enable)
        QTimer.singleShot(0, self.file_populate_open_recent_menu)


    def file_populate_open_recent_menu(self):
        self.file_open_recent_menu.clear()
        filenames = [filename for filename in
                     reversed(self.recent_files[-9:])
                     if pathlib.Path(filename).exists()]
        self.file_open_recent_menu.setEnabled(bool(filenames))
        icon = Config.path() / 'images/document-open.svg'
        for i, filename in enumerate(filenames, 1):
            action = make_action(
                self, icon, '&{} {}'.format(i, filename),
                lambda *_, filename=filename: self.file_load(filename))
            self.file_open_recent_menu.addAction(action)


    def file_new(self):
        print('file_new') # TODO


    def file_open(self):
        print('file_open') # TODO


    def file_save(self):
        print('file_save') # TODO


    def file_saveas(self):
        print('file_saveas') # TODO


    def file_backup(self):
        print('file_backup') # TODO


    def file_import(self):
        print('file_import') # TODO


    def file_export(self):
        print('file_export') # TODO


    def file_load(self, filename):
        with contextlib.suppress(ValueError):
            self.recent_files.remove(filename)
        print(f'file_load {filename}') # TODO
