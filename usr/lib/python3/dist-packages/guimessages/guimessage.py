#!/usr/bin/python3 -su

## Copyright (C) 2014 troubadour <trobador@riseup.net>
## Copyright (C) 2014 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

import sys
import signal

import yaml

from PyQt5 import QtGui, QtWidgets
from guimessages import translations


class gui_message(QtWidgets.QMessageBox):
    def __init__(self, file_path, section):
        super(gui_message, self).__init__()

        tr = translations._translations(file_path, section)

        stream = open(file_path, 'r')
        data = yaml.safe_load(stream)
        section = data[section]

        self.icon = section.get('icon', None)
        self.button = section.get('button', None)

        #if tr.section.get('position') == 'topleft':
            #self.move(0,0)

        self._ = tr.gettext
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QtGui.QIcon("/usr/share/icons/gnome/24x24/status/info.png"))

        self.setIcon(getattr(QtWidgets.QMessageBox, self.icon))
        self.setStandardButtons(getattr(QtWidgets.QMessageBox, self.button))

        self.setWindowTitle(self._('title'))
        self.setText(self._('message'))

        self.exec_()

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication(sys.argv)
    message = gui_message(sys.argv[1], sys.argv[2])
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

