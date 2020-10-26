#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import pathlib
import sys

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication

import Config
import MainWindow
from Const import APPNAME


def main():
    if len(sys.argv) > 1 and sys.argv[1] in {'-h', '--help'}:
        raise SystemExit(USAGE)
    app = QApplication(sys.argv)
    app.setOrganizationName('Mark Summerfield')
    app.setOrganizationDomain('qtrac.eu')
    app.setApplicationName(APPNAME)
    app.setApplicationVersion('0.1.0')
    config = Config.get(pathlib.Path(__file__).resolve().parent)
    app.setWindowIcon(QIcon(str(config.path / 'images/icon.svg')))
    filename = sys.argv[1] if len(sys.argv) == 2 else None
    window = MainWindow.Window(filename)
    window.show()
    sys.exit(app.exec_())


USAGE = f'''usage: {pathlib.Path(sys.argv[0]).name} [filename]

An easy to use GUI application for viewing, creating, editing, and updating
SQLite and Songbird databases.

filename must be a SQLite or Songbird database
         (typically .db, .db3, .sqlite, .sqlite3, .sb)'''


if __name__ == '__main__':
    main()
