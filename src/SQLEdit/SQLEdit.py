#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtWidgets import QPlainTextEdit

from . import SQLSyntaxHighlighter


class SQLEdit(QPlainTextEdit):

    def __init__(self, text=''):
        super().__init__(text)
        SQLSyntaxHighlighter.SQLSyntaxHighlighter(self.document())


    def sizeHint(self):
        return self.minimumSizeHint()
