#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import contextlib
import pathlib

from PySide2.QtCore import QStandardPaths
from PySide2.QtWidgets import QMainWindow, QMdiArea

from . import FileActions, HelpActions
from .Const import TIMEOUT_LONG
from .Util import add_actions


class Window(QMainWindow, FileActions.Mixin, HelpActions.Mixin):

    recent_files = [] # Order is Old to New; static for all main windows

    def __init__(self, app_path, filename):
        super().__init__()
        self.app_path = app_path
        self.path = self.export_path = QStandardPaths.writableLocation(
            QStandardPaths.DocumentsLocation)
        self.default_blink_rate = qApp.cursorFlashTime()
        self.closing = False
        self.setWindowTitle(
            f'{qApp.applicationName()} {qApp.applicationVersion()}')
        self.make_widgets()
        self.make_layout()
        self.make_actions()
        self.make_connections()
        qApp.commitDataRequest.connect(self.close)
        self.load_settings(filename)
        self.update_ui()


    def closeEvent(self, event):
        self.closing = True
        # if bool(self.model):
        #     self.add_recent_file(self.model.filename)
        # self.save_settings()
        # self.save()
        print('closeEvent: maybe unsaved changes dialog + '
              'save settings in .sbc file')
        event.accept()


    def load_settings(self, filename):
        print('load_settings')
        # settings = QSettings()
        # self.configure_blink_rate()
        # self.restoreGeometry(settings.value(SETTINGS_GEOMETRY,
        #                                     QByteArray()))
        # self.restoreState(settings.value(SETTINGS_WINDOW_STATE,
        #                                  QByteArray()))
        # Window.recent_files = settings.value(SETTINGS_RECENT_FILES) or []
        # if isinstance(Window.recent_files, str):
        #     Window.recent_files = [Window.recent_files]
        # if not filename:
        #     filename = settings.value(SETTINGS_LAST_FILE)
        if filename and not pathlib.Path(filename).exists():
            filename = None
        if filename:
            self.file_open(filename)
        else:
            self.statusBar().showMessage(
                'Click File→New or File→Open to open or create a database',
                TIMEOUT_LONG)


    def add_recent_file(self, filename):
        with contextlib.suppress(ValueError):
            Window.recent_files.remove(filename)
        Window.recent_files.append(filename)
        Window.recent_files = Window.recent_files[-9:]


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

        print('make_actions')

        self.make_help_actions()
        self.help_menu = self.menuBar().addMenu('&Help')
        add_actions(self.help_menu, self.help_actions_for_menu)


    def make_connections(self):
        print('make_connections')


    def update_ui(self):
        print('update_ui')
