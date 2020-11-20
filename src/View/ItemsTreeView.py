#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtGui import QBrush, Qt
from PySide2.QtWidgets import QHeaderView, QTreeWidget, QTreeWidgetItem

from TableWidget import TableWidget


class Mixin:

    def refresh_items(self):
        self.itemsTreeDock.widget().refresh()


    def maybe_show_item(self, item, _=None):
        if item.parent() is None:
            return # Ignore top-level items
        kind = item.parent().text(0).lower()[:-1]
        name = item.text(0)
        sub_window = self.findSubWindow(name)
        if sub_window is None:
            if kind in {'table', 'view'}:
                select = self.db.select_make(kind, name)
                widget = TableWidget(self.db, name, select,
                                     self.edit_update_ui)
                sub_window = self.mdiArea.addSubWindow(widget)
                widget.show()
            else:
                # TODO create a new QueryWidget or TriggerEditWidget etc.
                print('maybe_show_item', kind, name) # TODO
        if sub_window is not None:
            self.mdiArea.setActiveSubWindow(sub_window)


class View(QTreeWidget):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setHeaderHidden(True)
        self.setSelectionBehavior(QTreeWidget.SelectRows)
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setAlternatingRowColors(True)


    def refresh(self):
        self.clear()
        if bool(self.db):
            self._prepare()
            self.queryItem = QTreeWidgetItem(self, ('Queries',))
            tableItem = QTreeWidgetItem(self, ('Tables',))
            viewItem = QTreeWidgetItem(self, ('Views',))
            triggerItem = QTreeWidgetItem(self, ('Triggers',))
            indexItem = QTreeWidgetItem(self, ('Indexes',))
            firstItem = None
            for item in self.db.item_summary():
                new_item = QTreeWidgetItem((item.name,))
                if item.kind == 'table':
                    parent = tableItem
                    self._add_table_item(item.name, new_item, parent)
                    if firstItem is None:
                        firstItem = new_item
                elif item.kind == 'view':
                    parent = viewItem
                elif item.kind == 'trigger':
                    parent = triggerItem
                elif item.kind == 'index':
                    parent = indexItem
                parent.addChild(new_item)
            for item in (self.queryItem, tableItem, viewItem):
                if item.childCount() < 11:
                    self.expandItem(item)
            if firstItem is not None:
                self.setCurrentItem(firstItem)


    def _prepare(self):
        self.setColumnCount(2)
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)


    def _add_table_item(self, tablename, item, parent):
        for detail in self.db.item_detail(tablename):
            if detail.pk:
                color = Qt.darkGreen
            elif detail.notnull:
                color = Qt.black
            else:
                color = Qt.darkGray
            child = QTreeWidgetItem((detail.name, detail.type.upper()))
            child.setForeground(0, QBrush(color))
            font = child.font(1)
            font.setPointSize(max(6, font.pointSize() - 1))
            child.setFont(1, font)
            item.addChild(child)


    def copy(self):
        item = self.currentItem()
        if item is not None and item.parent() is not None:
            clipboard = qApp.clipboard()
            clipboard.setText(item.text(0))


    def canCopy(self):
        return self.can_view()


    def can_view(self):
        return (self.currentItem() is not None and
                self.currentItem().parent() is not None)
