#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.


class Mixin:

    def maybe_restore_ui(self):
        if not bool(self.db):
            return
        print('maybe_restore_ui', self.db.filename)


    def save_ui(self):
        if not bool(self.db):
            return
        print('save_ui         ', self.db.filename)
