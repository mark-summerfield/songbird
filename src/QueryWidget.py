#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtWidgets import QWidget


class Widget(QWidget):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.dirty = False


    def closeEvent(self):
        self.save(closing=True)


    def save(self, *, closing=False):
        # TODO what happens if there's an error and it can't save? We could
        # be closing down
        print(f'QueryModel Widget.save dirty={self.dirty} closing={closing}')
        if self.dirty and bool(self.model):
            pass # TODO
        self.dirty = False
