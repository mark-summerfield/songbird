#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtWidgets import QPlainTextEdit


class SQLEdit(QPlainTextEdit):

    def __init__(self, text=''):
        super().__init__(text)


    def sizeHint(self):
        return self.minimumSizeHint()
