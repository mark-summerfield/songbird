#!/usr/bin/env python3
# Copyright © 2020 Mark Summerfield. All rights reserved.

import pathlib
import sys

from PySide2.QtCore import QtMsgType, qInstallMessageHandler
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication

import Config
import MainWindow
from Const import APPNAME


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] in {'-h', '--help'}:
            raise SystemExit(USAGE)
        if sys.argv[1] in {'-D', '--debug'}:
            _messageHandler.debug = True
            sys.argv.pop(1)
    app = QApplication(sys.argv)
    app.setOrganizationName('Mark Summerfield')
    app.setOrganizationDomain('qtrac.eu')
    app.setApplicationName(APPNAME)
    app.setApplicationVersion('0.1.0')
    Config.initialize(pathlib.Path(__file__).resolve().parent)
    app.setWindowIcon(QIcon(str(Config.path() / 'images/icon.svg')))
    filename = sys.argv[1] if len(sys.argv) == 2 else None
    window = MainWindow.Window(filename)
    window.show()
    sys.exit(app.exec_())


USAGE = f'''usage: {pathlib.Path(sys.argv[0]).name} [filename]

An easy to use GUI application for viewing, creating, editing, and updating
SQLite and Songbird databases.

filename must be a SQLite or Songbird database
         (typically .db, .db3, .sqlite, .sqlite3, .sb)'''


def _messageHandler(kind, context, message):
    if _messageHandler.debug:
        if context.file and context.function:
            print(f'{_str_for_kind(kind)}: {message} '
                  f'({context.file}:{context.line} {context.function}())')
            return
    else:
        if kind == QtMsgType.QtDebugMsg:
            return
        if kind == QtMsgType.QtWarningMsg:
            lmessage = message.casefold()
            if 'unable to open default eudc font' in lmessage:
                return
            if 'is a null image' in lmessage:
                return
    print(f'{_str_for_kind(kind)}: {message}')
_messageHandler.debug = False # noqa


def _str_for_kind(kind):
    kind = kind.name.decode('utf-8')
    if kind.startswith('Qt'):
        kind = kind[2:]
    if kind.endswith('Msg'):
        kind = kind[:-3].upper()
    return kind


qInstallMessageHandler(_messageHandler)


if __name__ == '__main__':
    main()
