#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import datetime
import platform
import sys

import PySide2.QtCore
from PySide2.QtCore import QSysInfo
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QMessageBox

import apsw
from AppData import HELP_SVG, ICON_SVG, get_icon
from Const import APPNAME, VERSION
from Ui import make_action


class Mixin:

    def make_help_actions(self):
        self.help_action = make_action(
            self, get_icon(HELP_SVG), '&Help', self.help,
            QKeySequence.HelpContents, 'Show the online help')
        self.help_about_action = make_action(
            self, get_icon(ICON_SVG), '&About', self.help_about,
            tip=f"Show {APPNAME}'s about box")


    @property
    def help_actions_for_menu(self):
        return (self.help_action, self.help_about_action,)


    def help_about(self):
        year = datetime.date.today().year
        year = "2020-{}".format(str(year)[-2:]) if year != 2020 else "2020"
        TEMPLATE = ('Python&nbsp;{}.{}.{} <br> {} <br> {}'
                    '<br>APSW&nbsp;{} <br> SQLite&nbsp;{}<br>{}<br>{}')
        BINDING = f'PySide2&nbsp;{PySide2.__version__}'
        QT = f'Qt&nbsp;{PySide2.QtCore.qVersion()}'
        info = TEMPLATE.format(
            sys.version_info.major, sys.version_info.minor,
            sys.version_info.micro, BINDING, QT, apsw.apswversion(),
            apsw.sqlitelibversion(), QSysInfo.prettyProductName(),
            platform.platform())
        QMessageBox.about(
            self, f'About — {APPNAME}', f'''<p>
<font color=navy><b>{APPNAME} {VERSION}</b></font></p>
<p>
<font color=navy>{APPNAME} is an easy to learn and use GUI application for
viewing, creating, editing, and updating SQLite and {APPNAME} databases.
</font>
</p>
<p><a href="https://github.com/mark-summerfield/songbird">Source Code</a>
</p>
<p>Copyright © {year} Mark Summerfield.<br>
All Rights Reserved.</p>
<p>
This software is Free Open Source Software (FOSS) licensed under the
GNU Public License version 3 (GPLv3).
</p>
<hr>
<p><font color=teal>{info}</font></p>
'''.format(year=year, info=info)) # noqa


    def help(self):
        print('help') # TODO
