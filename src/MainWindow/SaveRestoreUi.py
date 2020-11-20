#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtWidgets import QMdiArea

import Config
from TableWidget import TableWidget


class Mixin:

    def maybe_restore_ui(self):
        if not bool(self.db):
            return
        if self.db.is_songbird:
            return # TODO restore from the db itself
        if (ui := Config.read_db_ui(self.db.filename)) is None:
            return # Haven't seen this database in past year
        self._restore_overall_ui(ui)
        self._restore_windows_ui(ui.windows)


    def _restore_overall_ui(self, ui):
        mode = self.mdiArea.viewMode()
        if ((ui.mdi and mode != QMdiArea.SubWindowView) or
             (not ui.mdi and mode != QMdiArea.TabbedView)):
            self.view_items_tree_toggle_tabs()
        if ui.show_items_tree != self.itemsTreeDock.isVisible():
            self.itemsTreeDock.setVisible(
                not self.itemsTreeDock.isVisible())
            self.view_update_toggle_action()
        if ui.show_pragmas != self.pragmasDock.isVisible():
            self.pragmasDock.setVisible(not self.pragmasDock.isVisible())
            self.view_pragmas_update_toggle_action()
        # TODO calendar


    def _restore_windows_ui(self, windows):
        for window in windows:
            widget = TableWidget(self.db, window.title, window.sql_select,
                                 self.edit_update_ui)
            sub_window = self.mdiArea.addSubWindow(widget)
            sub_window.setGeometry(window.x, window.y, window.width,
                                   window.height)
            widget.splitter.setSizes(window.sizes)
            widget.show()


    def maybe_save_ui(self):
        if not bool(self.db):
            return
        if self.db.is_songbird:
            return # TODO save to the db itself
        ui = Config.DbUi(self.db.filename)
        ui.mdi = self.mdiArea.viewMode() == QMdiArea.SubWindowView
        ui.show_items_tree = self.itemsTreeDock.isVisible()
        ui.show_pragmas = self.pragmasDock.isVisible()
        # ui.show_calendar = self.calendarDock.isVisible() # TODO
        for widget in self.mdiArea.subWindowList():
            child = widget.widget()
            if (child is not None and isinstance(child, TableWidget) and
                    child.is_select):
                rect = widget.geometry()
                ui.windows.append(Config.DbWindowUi(
                    widget.windowTitle(), child.sql, x=rect.x(), y=rect.y(),
                    width=rect.width(), height=rect.height(),
                    sizes=child.sizes))
        Config.write_db_ui(ui)
