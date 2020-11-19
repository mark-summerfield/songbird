#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import Config


class Mixin:

    def maybe_restore_ui(self):
        if not bool(self.db):
            return
        fileui = Config.read_file_ui(self.db.filename)
        print('maybe_restore_ui', vars(fileui)) # TODO delete
        if fileui is None: # Haven't seen this database in past year
            return
        # TODO apply to UI


    def maybe_save_ui(self):
        if not bool(self.db):
            return
        fileui = Config.FileUi(self.db.filename)
        # TODO populate from UI
        print('maybe_save_ui', vars(fileui))
        Config.write_file_ui(fileui)
