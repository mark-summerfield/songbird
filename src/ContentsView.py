#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import contextlib

import shiboken2
from PySide2.QtGui import QBrush, Qt
from PySide2.QtWidgets import QHeaderView, QTreeWidget, QTreeWidgetItem

import TableWidget


class Mixin:

    def refresh_contents(self):
        self.contentsDock.widget().refresh()


    def maybe_show_content(self, item, _=None):
        if item.parent() is None:
            return # Ignore top-level items
        kind = item.parent().text(0).lower()[:-1]
        name = item.text(0)
        sub_window = self.mdiWidgets.get((kind, name))
        if not shiboken2.isValid(sub_window):
            with contextlib.suppress(KeyError):
                del self.mdiWidgets[(kind, name)]
            sub_window = None
        if sub_window is None:
            if kind in {'table', 'view'}:
                select = self.db.select_make(kind, name)
                widget = TableWidget.TableWidget(self.db, name, select)
                widget.sqlEdit.textChanged.connect(self.edit_update_ui)
                sub_window = self.mdiArea.addSubWindow(widget)
                self.mdiWidgets[(kind, name)] = sub_window
                widget.show()
            else:
                # TODO create a new QueryWidget or TriggerEditWidget etc.
                print('maybe_show_content', kind, name) # TODO
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
            for content in self.db.content_summary():
                item = QTreeWidgetItem((content.name,))
                if content.kind == 'table':
                    parent = tableItem
                    self._add_table_item(content.name, item, parent)
                    if firstItem is None:
                        firstItem = item
                elif content.kind == 'view':
                    parent = viewItem
                elif content.kind == 'trigger':
                    parent = triggerItem
                elif content.kind == 'index':
                    parent = indexItem
                parent.addChild(item)
            self.expandItem(tableItem)
            if firstItem is not None:
                self.setCurrentItem(firstItem)
                self.expandItem(firstItem)


    def _prepare(self):
        self.setColumnCount(2)
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)


    def _add_table_item(self, tablename, item, parent):
        for detail in self.db.content_detail(tablename):
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
