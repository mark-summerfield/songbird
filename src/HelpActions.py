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
import Config
from Ui import make_action


class Mixin:

    def make_help_actions(self):
        path = Config.path()
        self.help_action = make_action(
            self, path / 'images/help.svg', '&Help', self.help,
            QKeySequence.HelpContents)
        self.help_about_action = make_action(
            self, path / 'images/icon.svg', '&About', self.help_about)


    @property
    def help_actions_for_menu(self):
        return (self.help_action, self.help_about_action,)


    def help_about(self):
        year = datetime.date.today().year
        year = "2020-{}".format(str(year)[-2:]) if year != 2020 else "2020"
        TEMPLATE = ('Python&nbsp;{}.{}.{} • {} • {}'
                    '<br>APSW&nbsp;{} • SQLite&nbsp;{}<br>{}<br>{}')
        BINDING = f'PySide2&nbsp;{PySide2.__version__}'
        QT = f'Qt&nbsp;{PySide2.QtCore.qVersion()}'
        info = TEMPLATE.format(
            sys.version_info.major, sys.version_info.minor,
            sys.version_info.micro, BINDING, QT, apsw.apswversion(),
            apsw.sqlitelibversion(), QSysInfo.prettyProductName(),
            platform.platform())
        # TODO change URL below to github
        QMessageBox.about(
            self, f'About — {qApp.applicationName()}', '''<p>
<font color=navy><b>{app} {version}</b></font></p>
<p>
<font color=navy>{app} is an easy to learn and use GUI application for
viewing, creating, editing, and updating SQLite and Songbird databases.
</font>
</p>
<p><a
href="http://www.qtrac.eu/songbird.html">www.qtrac.eu/songbird.html</a>
</p>
<p>Copyright © {year} Mark Summerfield.<br>
All Rights Reserved.</p>
<p>
This software is Free Open Source Software (FOSS) licensed under the
GNU Public License version 3 (GPLv3).
</p>
<hr>
<p><font color=teal>{info}</font></p>
'''.format(app=qApp.applicationName(), version=qApp.applicationVersion(),
           year=year, info=info)) # noqa


    def help(self):
        print('help') # TODO
