#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from PySide2.QtWidgets import QMessageBox, QWidget


class Widget(QWidget):

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.dirty = False


    def closeEvent(self):
        self.save(closing=True)


    def save(self, *, closing=False):
        print(f'QueryWidget.save dirty={self.dirty} closing={closing}')
        saved = not self.dirty
        errors = False
        if self.dirty and bool(self.model):
            # TODO save change to list view or form view
            errors = []# self.model.save_...
            if errors:
                if not closing:
                    error = '\n'.join(errors)
                    QMessageBox.warning(
                        self, f'Save error — {qApp.applicationName()}',
                        f'Failed to save:\n{error}')
            else:
                saved = True
        self.dirty = not errors
        return saved
