#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import Config


class Mixin:

    def maybe_restore_ui(self):
        if not bool(self.db):
            return
        ui = Config.read_db_ui(self.db.filename)
        print('maybe_restore_ui', vars(ui)) # TODO delete
        if ui is None: # Haven't seen this database in past year
            return
        # TODO apply to UI


    def maybe_save_ui(self):
        if not bool(self.db):
            return
        ui = Config.DbUi(self.db.filename)
        # TODO populate from UI
        print('maybe_save_ui', vars(ui))
        Config.write_db_ui(ui)
