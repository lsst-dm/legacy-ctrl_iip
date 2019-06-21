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
from lsst.ctrl.iip.ocs.messages.ATArchiverMessages import ATArchiverMessages
from lsst.ctrl.iip.ocs.messages.DefaultMessages import DefaultMessages


class ATArchiverMessagesTestCase(unittest.TestCase):

    def setUp(self):
        default = DefaultMessages()
        self.expected_commands = default.get_commands()
        self.expected_commands.append("resetFromFault")

        self.expected_log_events = default.get_log_events()
        self.expected_log_events.append("processingStatus")

        self.at_messages = ATArchiverMessages()

    def test_commands(self):
        commands = self.at_messages.get_commands()

        self.assertEqual(len(commands), len(self.expected_commands))
        for command in self.expected_commands:
            self.assertTrue(command in commands)

    def test_log_events(self):
        log_events = self.at_messages.get_log_events()

        self.assertEqual(len(log_events), len(self.expected_log_events))
        for log_event in self.expected_log_events:
            self.assertTrue(log_event in log_events)


if __name__ == "__main__":
    unittest.main()
