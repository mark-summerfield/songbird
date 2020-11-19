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
        ui = Config.read_db_ui(self.db.filename)
        print('maybe_restore_ui', ui) # TODO delete
        if ui is None: # Haven't seen this database in past year
            return
        # TODO apply to UI


    def maybe_save_ui(self):
        if not bool(self.db):
            return
        if self.db.is_songbird:
            return # TODO save to the db itself
        ui = Config.DbUi(self.db.filename)
        ui.mdi = self.mdiArea.viewMode() == QMdiArea.SubWindowView
        ui.show_items_tree = self.itemsTreeDock.isVisible()
        ui.show_pragmas = self.pragmasDock.isVisible()
        # ui.show_calendar = self.calendarDock.isVisible()
        for widget in self.mdi_widgets:
            child = widget.widget()
            if (child is not None and isinstance(child, TableWidget) and
                    child.is_select):
                ui.windows.append(Config.DbWindowUi(
                    widget.windowTitle(), child.sql, x=widget.x(),
                    y=widget.y(), width=widget.width(),
                    height=widget.height(),
                    editor_height=child.editor_height))
        Config.write_db_ui(ui)
