#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

import unittest

from PyQt5 import QtWidgets

from omtests.qt4gui.dialogs.base_test_dialog import BaseTestDialog

from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.qt4gui.dialogs.base_dialogs import HorizontalBaseDialog
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog


class TestDialog1(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''
    dl_class = BaseDialog

    def test_exec(self):
        self.init()
        self.dl.insertWidget(QtWidgets.QLabel("simple dialog"))
        self.exec_()


class TestDialog2(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''
    dl_class = BaseDialog

    def test_exec(self):
        self.init(remove_stretch=True)
        self.dl.insertWidget(QtWidgets.QLabel("simple dialog - no stretch"))
        self.exec_()


class TestDialog3(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''
    dl_class = HorizontalBaseDialog

    def test_exec(self):
        self.init()
        self.dl.insertWidget(QtWidgets.QLabel("horizontal dialog"))
        self.exec_()


class TestDialog4(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''
    dl_class = HorizontalBaseDialog

    def test_exec(self):
        self.init(remove_stretch=True)
        self.dl.insertWidget(QtWidgets.QLabel("horizontal dialog - no stretch"))
        self.exec_()


class TestDialog5(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''
    dl_class = ExtendableDialog

    def test_exec(self):
        self.init()
        self.dl.insertWidget(QtWidgets.QLabel("extendable dialog"))
        self.dl.insertWidget(QtWidgets.QLabel("extendable dialog - label2"))
        self.dl.add_advanced_widget(QtWidgets.QLabel("advanced options"))
        self.exec_()


class TestDialog6(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''
    dl_class = ExtendableDialog

    def test_exec(self):
        self.init(remove_stretch=True)
        self.dl.insertWidget(QtWidgets.QLabel("extendable dialog - no stretch"))
        self.dl.insertWidget(QtWidgets.QLabel("extendable dialog - label2"))
        self.dl.add_advanced_widget(QtWidgets.QLabel("advanced options"))
        self.exec_()


if __name__ == "__main__":
    unittest.main()
