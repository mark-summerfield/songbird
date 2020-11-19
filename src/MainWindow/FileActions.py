#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import pathlib

from PySide2.QtCore import QTimer
from PySide2.QtGui import QKeySequence, Qt
from PySide2.QtWidgets import QFileDialog, QMenu, QMessageBox

from AppData import (
    DOCUMENT_NEW_SVG, DOCUMENT_OPEN_SVG, EDIT_CLEAR_SVG, EXPORT_SVG,
    FILESAVE_SVG, FILESAVEAS_SVG, IMPORT_SVG, SHUTDOWN_SVG, get_icon)
from Const import APPNAME, SUFFIX, SUFFIX_DEFAULT, SUFFIXES, TIMEOUT_SHORT
from Ui import make_action


class Mixin:

    def make_file_actions(self):
        self.file_new_action = make_action(
            self, get_icon(DOCUMENT_NEW_SVG), '&New...', self.file_new,
            QKeySequence.New, f'Create a new SQLite or {APPNAME} database')
        self.file_open_action = make_action(
            self, get_icon(DOCUMENT_OPEN_SVG), '&Open...', self.file_open,
            QKeySequence.Open,
            f'Open an existing SQLite or {APPNAME} database')
        self.file_open_recent_action = make_action(
            self, get_icon(DOCUMENT_OPEN_SVG), 'Open &Recent')
        self.file_open_recent_menu = QMenu(self)
        self.file_open_recent_action.setMenu(self.file_open_recent_menu)
        self.file_save_action = make_action(
            self, get_icon(FILESAVE_SVG), '&Save', self.file_save,
            QKeySequence.Save, 'Save any unsaved changes to the database')
        self.file_saveas_action = make_action(
            self, get_icon(FILESAVEAS_SVG), 'Save &As...', self.file_saveas,
            QKeySequence.SaveAs, 'Save the database under a new name and '
            'open the database with the new name')
        self.file_backup_action = make_action(
            self, get_icon(FILESAVEAS_SVG), '&Backup...', self.file_backup,
            tip='Save a copy of the database')
        self.file_import_action = make_action(
            self, get_icon(IMPORT_SVG), '&Import...', self.file_import,
            tip='Import an external data file (e.g., CSV) as a new '
            'table in the current database')
        self.file_export_action = make_action(
            self, get_icon(EXPORT_SVG), '&Export...', self.file_export,
            tip="Export a table, view or SELECT query's data as an "
            'external data file (e.g., CSV)')
        self.file_quit_action = make_action(
            self, get_icon(SHUTDOWN_SVG), '&Quit', self.close,
            QKeySequence(Qt.CTRL + Qt.Key_Q),
            'Save any unsaved changes and quit')


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
        enable = bool(self.db)
        for action in (self.file_save_action, self.file_saveas_action,
                       self.file_backup_action, self.file_export_action):
            action.setEnabled(enable)
        QTimer.singleShot(0, self.file_populate_open_recent_menu)


    def file_populate_open_recent_menu(self):
        self.file_open_recent_menu.clear()
        filenames = [str(filename) for filename in list(self.recent_files)]
        self.file_open_recent_menu.setEnabled(bool(filenames))
        icon = get_icon(DOCUMENT_OPEN_SVG)
        for i, filename in enumerate(filenames, 1):
            action = make_action(
                self, icon, '&{} {}'.format(i, filename),
                lambda *_, filename=filename: self.file_load(filename),
                tip=f'Open {filename}')
            self.file_open_recent_menu.addAction(action)
        if filenames:
            self.file_open_recent_menu.addSeparator()
            self.file_open_recent_menu.addAction(make_action(
                self, get_icon(EDIT_CLEAR_SVG), '&Clear',
                self.file_clear_recent_files,
                tip='Clear the list of recently opened databases'))


    def file_clear_recent_files(self):
        self.recent_files.clear()
        self.file_update_ui()


    def file_new(self):
        if filename := self._file_new_or_open('New',
                                              QFileDialog.getSaveFileName):
            if filename.exists():
                QMessageBox.warning(
                    self, f'Database exists — {APPNAME}',
                    f'Will not overwrite an existing database '
                    '({filename}) with a new one')
            else:
                self.file_load(filename, new=True)


    def file_open(self):
        if filename := self._file_new_or_open('Open',
                                              QFileDialog.getOpenFileName):
            if not filename.exists():
                QMessageBox.warning(self, f'Database missing — {APPNAME}',
                                    f'Cannot find database {filename}')
            else:
                self.file_load(filename)


    def _file_new_or_open(self, prefix, dialog):
        suffixes = '*' + ' *'.join(SUFFIXES)
        filename, _ = dialog(self, f'{prefix} database — {APPNAME}',
                             str(self.path),
                             f'SQLite ({suffixes});;{APPNAME} ({SUFFIX});;'
                             'Any file (*.*)')
        if filename:
            filename = pathlib.Path(filename)
            self.path = filename.parent
            if '.' not in filename.name:
                filename = filename.with_suffix(SUFFIX_DEFAULT)
        return filename


    def file_load(self, filename, new=False):
        self.clear() # Will save if necessary
        self.db.open(filename) # previous is automatically closed
        self.recent_files.add(filename)
        filename = pathlib.Path(filename).resolve()
        self.setWindowTitle(f'{filename.name} — {APPNAME}')
        message = (f'Created new empty database {filename}' if new else
                   f'Opened database {filename}')
        self.statusBar().showMessage(message, TIMEOUT_SHORT)
        self.refresh_items()
        self.refresh_pragmas()
        self.maybe_restore_ui()
        self.update_ui()


    def file_save(self):
        saved = 0
        if bool(self.db):
            saved += self.pragmasDock.widget().save()
            for widget in self.mdi_widgets:
                saved += widget.save()
        message = 'Saved changes' if saved else 'No changes to save'
        self.statusBar().showMessage(message, TIMEOUT_SHORT)


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
