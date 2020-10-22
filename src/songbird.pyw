#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import pathlib
import sys

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication

from Gui.MainWindow import Window


def main():
    if len(sys.argv) > 1 and sys.argv[1] in {'-h', '--help'}:
        raise SystemExit(USAGE)
    app = QApplication(sys.argv)
    app.setOrganizationName('Mark Summerfield')
    app.setOrganizationDomain('qtrac.eu')
    app.setApplicationName('Songbird')
    app.setApplicationVersion('0.1.0')
    app_path = pathlib.Path(__file__).resolve().parent
    app.setWindowIcon(QIcon(str(app_path / 'images/icon.svg')))
    filename = sys.argv[1] if len(sys.argv) == 2 else None
    window = Window.Window(app_path, filename)
    window.show()
    sys.exit(app.exec_())


USAGE = f'''usage: {pathlib.Path(sys.argv[0]).name} [filename]

A GUI application for viewing, creating, and modifying
SQLite and Songbird databases.

filename must be a SQLite or Songbird database
         (typically .db, .db3, .sqlite, .sqlite3, .sb)'''


if __name__ == '__main__':
    main()
