#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtGui import QBrush, QColor
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem


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
        self.setRootIsDecorated(False)
        self.setSelectionBehavior(QTreeWidget.SelectRows)
        self.setSelectionMode(QTreeWidget.SingleSelection)


    def refresh(self):
        self.clear()
        if bool(self.model):
            self.setColumnCount(1)
            queryItem = QTreeWidgetItem(self, ('Queries',))
            tableItem = QTreeWidgetItem(self, ('Tables',))
            viewItem = QTreeWidgetItem(self, ('Views',))
            triggerItem = QTreeWidgetItem(self, ('Triggers',))
            indexItem = QTreeWidgetItem(self, ('Indexes',))
            firstItem = None
            for i, item in enumerate((queryItem, tableItem, viewItem,
                                      triggerItem, indexItem)):
                color = QColor('#F0F0F0' if i % 2 else '#E0E0E0')
                item.setBackground(0, QBrush(color))
            for content in self.model.content_summary():
                item = QTreeWidgetItem((content.name,))
                if content.kind == 'table':
                    parent = tableItem
                    if firstItem is None:
                        firstItem = item
                elif content.kind == 'view':
                    parent = viewItem
                elif content.kind == 'trigger':
                    parent = triggerItem
                elif content.kind == 'index':
                    parent = indexItem
                parent.addChild(item)
            self.expandAll()
            if firstItem is not None:
                self.setCurrentItem(firstItem)


    def copy(self):
        item = self.currentItem()
        if item is not None:
            clipboard = qApp.clipboard()
            clipboard.setText(item.text(0))


    def canCopy(self):
        return self.currentItem() is not None


    def can_view(self):
        return (self.currentItem() is not None and
                self.currentItem().parent() is not None)
