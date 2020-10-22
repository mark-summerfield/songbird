#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.


from PySide2.QtGui import QKeySequence, Qt

from .Util import make_action


class Mixin:

    def make_file_actions(self):
        self.file_quit_action = make_action(
            self, self.app_path / 'images/shutdown.svg', '&Quit',
            self.close, QKeySequence(Qt.CTRL + Qt.Key_Q))
        print('make_file_actions')


    @property
    def file_actions_for_menu(self):
        print('file_actions_for_menu')
        return (self.file_quit_action,)


    @property
    def file_actions_for_toolbar(self):
        print('file_actions_for_toolbar')
        return (self.file_quit_action,) # TODO don't include Quit in toolbar


    def file_open(self, filename):
        print(f'file_open {filename}')
