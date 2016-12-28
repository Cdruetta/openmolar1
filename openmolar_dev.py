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

'''
This executable script simply imports openmolar.main and calls run().

Since openmolar version 0.7 requires python 3 to run, warnings are given if
this is called with python2.
'''

import os
import sys

if sys.version < '3.0':
    sys.exit("This program requires a python3 runtime")

if __name__ == "__main__":
    DEV_MODULE = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "src"))
    print("openmolar_dev called using %s as DEV_MODULE" % DEV_MODULE)
    sys.path.insert(0, DEV_MODULE)

    from openmolar import main
    main.run()
