#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import pathlib

from PySide2.QtCore import QTimer
from PySide2.QtGui import QKeySequence, Qt
from PySide2.QtWidgets import QFileDialog, QMenu, QMessageBox

import Config
from Const import DEFAULT_SUFFIX, SUFFIX, SUFFIXES, TIMEOUT_SHORT
from Ui import make_action


class Mixin:

    def make_file_actions(self):
        path = Config.path() / 'images'
        self.file_new_action = make_action(
            self, path / 'document-new.svg', '&New...', self.file_new,
            QKeySequence.New)
        self.file_open_action = make_action(
            self, path / 'document-open.svg', '&Open...', self.file_open,
            QKeySequence.Open)
        self.file_open_recent_action = make_action(
            self, path / 'document-open.svg', 'Open &Recent')
        self.file_open_recent_menu = QMenu(self)
        self.file_open_recent_action.setMenu(self.file_open_recent_menu)
        self.file_save_action = make_action(
            self, path / 'filesave.svg', '&Save', self.file_save,
            QKeySequence.Save)
        self.file_saveas_action = make_action(
            self, path / 'filesaveas.svg', 'Save &As...', self.file_saveas,
            QKeySequence.SaveAs)
        self.file_backup_action = make_action(
            self, path / 'filesaveas.svg', '&Backup...', self.file_backup)
        self.file_import_action = make_action(
            self, path / 'import.svg', '&Import...', self.file_import)
        self.file_export_action = make_action(
            self, path / 'export.svg', '&Export...', self.file_export)
        self.file_quit_action = make_action(
            self, path / 'shutdown.svg', '&Quit', self.close,
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
        filenames = [str(filename) for filename in list(self.recent_files)]
        self.file_open_recent_menu.setEnabled(bool(filenames))
        icon = Config.path() / 'images/document-open.svg'
        for i, filename in enumerate(filenames, 1):
            action = make_action(
                self, icon, '&{} {}'.format(i, filename),
                lambda *_, filename=filename: self.file_load(filename))
            self.file_open_recent_menu.addAction(action)
        if filenames:
            self.file_open_recent_menu.addSeparator()
            self.file_open_recent_menu.addAction(make_action(
                self, Config.path() / 'images/edit-clear.svg', '&Clear',
                self.file_clear_recent_files))


    def file_clear_recent_files(self):
        self.recent_files.clear()
        self.file_update_ui()


    def file_new(self):
        filename = self._file_new_or_open('New',
                                          QFileDialog.getSaveFileName)
        if filename:
            if filename.exists():
                QMessageBox.warning(
                    self, f'Database exists — {qApp.applicationName()}',
                    f'Will not overwrite an existing database '
                    '({filename}) with a new one')
            else:
                self.file_load(filename, new=True)


    def file_open(self):
        filename = self._file_new_or_open('Open',
                                          QFileDialog.getOpenFileName)
        if filename:
            if not filename.exists():
                QMessageBox.warning(
                    self, f'Database missing — {qApp.applicationName()}',
                    f'Cannot find database {filename}')
            else:
                self.file_load(filename)


    def _file_new_or_open(self, prefix, dialog):
        suffixes = '*' + ' *'.join(SUFFIXES)
        filename, _ = dialog(
            self, f'{prefix} database — {qApp.applicationName()}',
            str(self.path),
            f'SQLite ({suffixes});;{qApp.applicationName()} ({SUFFIX});;'
            'Any file (*.*)')
        if filename:
            filename = pathlib.Path(filename)
            self.path = filename.parent
            if '.' not in filename.name:
                filename = filename.with_suffix(DEFAULT_SUFFIX)
        return filename


    def file_load(self, filename, new=False):
        self.clear() # Will save if necessary
        self.model.open(filename) # previous is automatically closed
        self.recent_files.add(filename)
        filename = pathlib.Path(filename).resolve()
        self.setWindowTitle(f'{filename.name} — {qApp.applicationName()}')
        message = (f'Created new empty database {filename}' if new else
                   f'Opened existing database {filename}')
        self.statusBar().showMessage(message, TIMEOUT_SHORT)
        self.refresh_contents()
        self.refresh_pragmas()
        self.update_ui()


    def file_save(self):
        if bool(self.model):
            widget = self.pragmasDock.widget()
            if widget is not None:
                widget.save()
            for widget in self.mdiWidgets.values():
                widget.save()


    def file_saveas(self):
        # self.recent_files.add(filename) # unless we use file_load()
        print('file_saveas') # TODO
        # save as and backup are the same except that for save as we then
        # open the file under the new name


    def file_backup(self):
        print('file_backup') # TODO


    def file_import(self):
        print('file_import') # TODO


    def file_export(self):
        print('file_export') # TODO
