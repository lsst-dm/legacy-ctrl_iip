# This file is part of ctrl_iip
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest
from lsst.ctrl.iip.ocs.Action import Action


class Retriever:
    def __init__(self):
        self.name = "retriever test"


class ActionTestCase(unittest.TestCase):

    def testAction(self):
        action = Action("device_name", "message", Retriever(), self.ack_method)

        self.assertEqual(action.device_name, "device_name")
        self.assertEqual(action.message, "message")
        self.assertEqual(action.message_retriever.name, "retriever test")
        self.assertEqual(action.ack_method, self.ack_method)

    def ack_method(self):
        pass


if __name__ == "__main__":
    unittest.main()
