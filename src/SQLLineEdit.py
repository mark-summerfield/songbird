#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtWidgets import QLineEdit


class SQLLineEdit(QLineEdit):

    def __init__(self, text=''):
        super().__init__(text)
