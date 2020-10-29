#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtGui import QBrush, Qt
from PySide2.QtWidgets import QHeaderView, QTreeWidget, QTreeWidgetItem


class Mixin:

    def refresh_contents(self):
        view = self.contentsDock.widget()
        if view is not None:
            view.refresh()


    def maybe_show_content(self, item, _=None):
        if item.parent() is None:
            return # Ignore top-level items
        kind = item.parent().text(0).lower()[:-1]
        name = item.text(0)
        print('maybe_show_content', kind, name) # TODO
        # either bring the MDI window showing this to the top or create an
        # MDI window and bring it to the top


class View(QTreeWidget):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setHeaderHidden(True)
        self.setSelectionBehavior(QTreeWidget.SelectRows)
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setAlternatingRowColors(True)


    def refresh(self):
        self.clear()
        if bool(self.model):
            self._prepare()
            self.queryItem = QTreeWidgetItem(self, ('Queries',))
            tableItem = QTreeWidgetItem(self, ('Tables',))
            viewItem = QTreeWidgetItem(self, ('Views',))
            triggerItem = QTreeWidgetItem(self, ('Triggers',))
            indexItem = QTreeWidgetItem(self, ('Indexes',))
            firstItem = None
            for content in self.model.content_summary():
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
        for detail in self.model.content_detail(tablename):
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
