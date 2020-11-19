#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import pathlib

import shiboken2
from PySide2.QtCore import QStandardPaths, Qt, QTimer
from PySide2.QtWidgets import QMainWindow, QMdiArea

import Config
import Db
import RecentFiles
from Const import APPNAME, RECENT_FILES_MAX, TIMEOUT_LONG, VERSION
from Ui import add_actions, make_dock_widget
from View import ItemsTreeView, PragmaView

from . import (
    EditActions, FileActions, HelpActions, OptionsActions, ViewActions,
    SaveRestoreUi)


class Window(QMainWindow, EditActions.Mixin, FileActions.Mixin,
             HelpActions.Mixin, ItemsTreeView.Mixin, OptionsActions.Mixin,
             PragmaView.Mixin, ViewActions.Mixin, SaveRestoreUi.Mixin):

    def __init__(self, filename):
        super().__init__()
        self.setWindowTitle(f'{APPNAME} {VERSION}')
        self.make_variables()
        self.make_widgets()
        self.make_actions()
        self.make_connections()
        qApp.commitDataRequest.connect(self.close)
        options = self.load_options(filename)
        self.update_ui()
        QTimer.singleShot(0, lambda: self.initalize_toggle_actions(options))


    def closeEvent(self, event):
        self.closing = True
        options = Config.MainWindowOptions(
            state=self.saveState(),
            geometry=self.saveGeometry(),
            last_filename=str(self.db.filename or ''),
            recent_files=list(self.recent_files),
            show_items_tree=self.itemsTreeDock.isVisible(),
            show_pragmas=self.pragmasDock.isVisible(),
            show_as_tabs=self.mdiArea.viewMode() == QMdiArea.TabbedView)
        Config.write_main_window_options(options)
        self.clear()
        event.accept()


    def make_variables(self):
        self.db = Db.Db()
        self.path = self.export_path = QStandardPaths.writableLocation(
            QStandardPaths.DocumentsLocation)
        self.recent_files = RecentFiles.get(RECENT_FILES_MAX)
        self.closing = False
        self.mdiWidgets = {} # key = (kind, name); value = QueryWidget etc.


    def make_widgets(self):
        self.mdiArea = QMdiArea()
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.setCentralWidget(self.mdiArea)
        allowedAreas = Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
        view = ItemsTreeView.View(self.db)
        self.itemsTreeDock = make_dock_widget(
            self, 'Items Tree', view, Qt.LeftDockWidgetArea, allowedAreas)
        view = PragmaView.View(self.db)
        self.pragmasDock = make_dock_widget(
            self, 'Pragmas', view, Qt.RightDockWidgetArea, allowedAreas)
        # TODO Calendar dock widget


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

        self.make_view_actions()
        self.view_menu = self.menuBar().addMenu('&View')
        add_actions(self.view_menu, self.view_actions_for_menu)
        self.view_toolbar = self.addToolBar('View')
        self.view_toolbar.setObjectName('View')
        add_actions(self.view_toolbar, self.view_actions_for_toolbar)

        # TODO record actions & database actions & (sdi) window actions +
        # update OptionsActions options_restore_toolbars()

        self.make_options_actions()
        self.options_menu = self.menuBar().addMenu('&Options')
        add_actions(self.options_menu, self.options_actions_for_menu)
        # self.options_toolbar = self.addToolBar('Options')
        # self.options_toolbar.setObjectName('Options')
        # add_actions(self.options_toolbar, self.options_actions_for_toolbar)

        self.make_help_actions()
        self.help_menu = self.menuBar().addMenu('&Help')
        add_actions(self.help_menu, self.help_actions_for_menu)


    def make_connections(self):
        widget = self.itemsTreeDock.widget()
        widget.itemDoubleClicked.connect(self.maybe_show_item)
        widget.itemSelectionChanged.connect(self.view_update_ui)
        # TODO


    def load_options(self, filename):
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
        return options


    def initalize_toggle_actions(self, options):
        self.itemsTreeDock.setVisible(options.show_items_tree)
        self.view_update_toggle_action(options.show_items_tree)
        show_pragmas = bool(self.db) and options.show_pragmas
        self.pragmasDock.setVisible(show_pragmas)
        self.view_pragmas_update_toggle_action(show_pragmas)
        self.mdiArea.setViewMode(
            QMdiArea.SubWindowView if options.show_as_tabs else
            QMdiArea.TabbedView) # Start with the opposite
        self.view_items_tree_toggle_tabs() # Toggle to correct & set action


    def update_ui(self):
        self.file_update_ui()
        self.edit_update_ui()
        self.view_update_ui()
        # TODO record & database & (sdi) window actions
        self.options_update_ui()


    def clear(self):
        self.save_ui()
        widget = self.pragmasDock.widget()
        widget.save(closing=self.closing)
        widget.clear()
        for widget in self.mdi_widgets:
            widget.close() # Will save if dirty
        self.mdiWidgets.clear()


    @property
    def mdi_widgets(self):
        to_delete = []
        widgets = []
        for key, widget in self.mdiWidgets.items():
            if shiboken2.isValid(widget):
                widgets.append(widget)
            else:
                to_delete.append(key)
        for key in to_delete:
            del self.mdiWidgets[key]
        return widgets
