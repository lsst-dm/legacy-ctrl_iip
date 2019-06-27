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
from lsst.ctrl.iip.ocs.messages.Messages import Messages


class MessagesTestCase(unittest.TestCase):

    def setUp(self):
        self.messages = Messages()

    def testMessages(self):
        self.assertEqual(len(self.messages.get_commands()), 0)
        self.assertEqual(len(self.messages.get_events()), 0)
        self.assertEqual(len(self.messages.get_log_events()), 0)
        self.assertEqual(len(self.messages.get_command_acks()), 0)

        with self.assertRaises(AttributeError):
            composer = self.messages.get_composer("foo")  # noqa: F841

    def ack_method(self):
        pass


if __name__ == "__main__":
    unittest.main()
