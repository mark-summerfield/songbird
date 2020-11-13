#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

from AppData import EMBLEM_SYMBOLIC_LINK_SVG, get_icon
from Ui import make_action

# Restore &Toolbars
# &Options... TODO


class Mixin:

    def make_options_actions(self):
        self.options_restore_toolbars_action = make_action(
            self, get_icon(EMBLEM_SYMBOLIC_LINK_SVG), 'Restore &Toolbars',
            self.options_restore_toolbars, tip='Make every toolbar visible')
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
