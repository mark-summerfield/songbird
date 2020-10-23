#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.


from PySide2.QtGui import QKeySequence, Qt
from PySide2.QtWidgets import QMenu

from .Util import make_action


class Mixin:

    def make_file_actions(self):
        self.file_new_action = make_action(
            self, self.app_path / 'images/document-new.svg', '&New...',
            self.file_new, QKeySequence.New)
        self.file_open_action = make_action(
            self, self.app_path / 'images/document-open.svg', '&Open...',
            self.file_open, QKeySequence.Open)
        self.file_open_recent_action = make_action(
            self, self.app_path / 'images/document-open.svg',
            'Open &Recent')
        self.file_open_recent_menu = QMenu(self)
        self.file_open_recent_action.setMenu(self.file_open_recent_menu)
        self.file_save_action = make_action(
            self, self.app_path / 'images/filesave.svg', '&Save',
            self.file_save, QKeySequence.Save)
        self.file_saveas_action = make_action(
            self, self.app_path / 'images/filesaveas.svg', 'Save &As...',
            self.file_saveas, QKeySequence.SaveAs)
        self.file_backup_action = make_action(
            self, self.app_path / 'images/filesaveas.svg', '&Backup...',
            self.file_backup)
        self.file_import_action = make_action(
            self, self.app_path / 'images/import.svg', '&Import...',
            self.file_import)
        self.file_export_action = make_action(
            self, self.app_path / 'images/export.svg', '&Export...',
            self.file_export)
        self.file_quit_action = make_action(
            self, self.app_path / 'images/shutdown.svg', '&Quit',
            self.close, QKeySequence(Qt.CTRL + Qt.Key_Q))


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
        print('file_update_ui') # TODO


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
        print(f'file_load {filename}') # TODO
