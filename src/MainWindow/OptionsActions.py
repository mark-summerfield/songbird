#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import Config
from Ui import make_action

# Restore &Toolbars
# [ ] Show C&alendar TODO
# &Options... TODO


class Mixin:

    def make_options_actions(self):
        path = Config.path() / 'images'
        self.options_restore_toolbars_action = make_action(
            self, path / 'emblem-symbolic-link.svg', 'Restore &Toolbars',
            self.options_restore_toolbars)
        # TODO


    @property
    def options_actions_for_menu(self):
        # TODO
        return (self.options_restore_toolbars_action,)


    @property
    def options_actions_for_toolbar(self):
        # TODO and if non-empty update options_restore_toolbars() below
        return ()


    def options_update_ui(self):
        # TODO
        pass


    def options_restore_toolbars(self):
        for toolbar in (self.file_toolbar, self.edit_toolbar,
                        self.view_toolbar):
            if toolbar.isHidden():
                toolbar.show()
