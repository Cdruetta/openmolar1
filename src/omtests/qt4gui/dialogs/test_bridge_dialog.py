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

from openmolar.qt4gui.dialogs.bridge_dialog import BridgeDialog


class Duckling:
    is_Static = False


class Duck:
    toothPropsWidget = Duckling()


class TestDialog(BaseTestDialog):
    '''
    BaseTestDialog inherits from unittest.TestCase
    '''

    dl_class = BridgeDialog

    def test_exec(self):
        mw = QtWidgets.QWidget()
        mw.ui = Duck()
        self.exec_(mw)
        print(self.dl.chosen_treatments)


if __name__ == "__main__":
    unittest.main()
