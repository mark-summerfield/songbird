#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import pathlib

from PySide2.QtCore import QStandardPaths
from PySide2.QtWidgets import QMainWindow, QMdiArea

import Config
import EditActions
import FileActions
import HelpActions
import Model
import RecentFiles
from Const import BLINK, RECENT_FILES_MAX, TIMEOUT_LONG
from Ui import add_actions


class Window(QMainWindow, EditActions.Mixin, FileActions.Mixin,
             HelpActions.Mixin):

    def __init__(self, filename):
        super().__init__()
        self.model = Model.Model()
        self.path = self.export_path = QStandardPaths.writableLocation(
            QStandardPaths.DocumentsLocation)
        self.recent_files = RecentFiles.RecentFiles(RECENT_FILES_MAX)
        self.default_blink_rate = qApp.cursorFlashTime()
        self.closing = False
        self.setWindowTitle(
            f'{qApp.applicationName()} {qApp.applicationVersion()}')
        self.make_widgets()
        self.make_layout()
        self.make_actions()
        self.make_connections()
        qApp.commitDataRequest.connect(self.close)
        self.load_options(filename)
        self.update_ui()


    def closeEvent(self, event):
        self.closing = True
        print('closeEvent: maybe unsaved changes dialog')
        self.file_save() # TODO maybe save?
        options = Config.MainWindowOptions(
            self.saveState(), self.saveGeometry(),
            str(self.model.filename or ''), list(self.recent_files))
        Config.write_main_window_options(options)
        event.accept()


    def load_options(self, filename):
        qApp.setCursorFlashTime(self.default_blink_rate
                                if Config.get(BLINK) else 0)
        options = Config.read_main_window_options()
        if options.state is not None:
            self.restoreState(options.state)
        if options.geometry is not None:
            self.restoreGeometry(options.geometry)
        self.recent_files.load(options.recent_files)
        if (not filename and options.last_filename and
                pathlib.Path(options.last_filename).exists()):
            filename = options.last_filename
        if filename and not pathlib.Path(filename).exists():
            filename = None
        if filename:
            if options.last_filename:
                self.recent_files.add(options.last_filename)
            self.file_load(filename)
        else:
            self.statusBar().showMessage(
                'Click File→New or File→Open to open or create a database',
                TIMEOUT_LONG)


    def make_widgets(self):
        self.mdiArea = QMdiArea()
        self.setCentralWidget(self.mdiArea)
        # TODO contents tree dock widget + MDI central area
        print('make_widgets')


    def make_layout(self):
        print('make_layout')


    def make_actions(self):
        self.make_file_actions()
        self.file_menu = self.menuBar().addMenu('&File')
        add_actions(self.file_menu, self.file_actions_for_menu)
        self.file_toolbar = self.addToolBar('File')
        self.file_toolbar.setObjectName('File')
        add_actions(self.file_toolbar, self.file_actions_for_toolbar)

        self.make_edit_actions()
        self.edit_menu = self.menuBar().addMenu('&Edit')
        add_actions(self.edit_menu, self.edit_actions_for_menu)
        self.edit_toolbar = self.addToolBar('Edit')
        self.edit_toolbar.setObjectName('Edit')
        add_actions(self.edit_toolbar, self.edit_actions_for_toolbar)

        print('make_actions')

        self.make_help_actions()
        self.help_menu = self.menuBar().addMenu('&Help')
        add_actions(self.help_menu, self.help_actions_for_menu)


    def make_connections(self):
        print('make_connections')


    def update_ui(self):
        self.file_update_ui()
        self.edit_update_ui()
        print('update_ui')
