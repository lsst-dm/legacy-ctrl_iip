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
from lsst.ctrl.iip.ocs.messages.EFDMessages import EFDMessages
import SALPY_EFD


class EFDMessagesTestCase(unittest.TestCase):

    def setUp(self):
        self.efd_messages = EFDMessages()
        self.expected_events = ["largeFileObjectAvailable"]

        self.byte_size = 12
        self.check_sum = "88"
        self.generator = "camera"
        self.mime_type = "raw"
        self.url = "https://www.lsst.org/sites/default/files/logo_1.png"
        self.version = 1
        self.id = "8675309"
        self.priority = 1

    def test_commands(self):
        commands = self.efd_messages.get_commands()
        self.assertEqual(len(commands), 0)

    def test_log_events(self):
        log_events = self.efd_messages.get_log_events()
        self.assertEqual(len(log_events), 0)

    def test_events(self):

        events = self.efd_messages.get_events()
        self.assertEqual(len(self.expected_events), len(events))

        for expected in self.expected_events:
            self.assertTrue(expected in events)

    def test_largeFileObjectAvailable_message(self):

        data = SALPY_EFD.EFD_logevent_largeFileObjectAvailableC()
        data.byteSize = self.byte_size
        data.checkSum = self.check_sum
        data.generator = self.generator
        data.mimeType = self.mime_type
        data.url = self.url
        data.version = self.version
        data.id = self.id
        data.priority = self.priority

        msg = self.efd_messages.build_largeFileObjectAvailable_message(data)

        self.assertEqual(msg["MSG_TYPE"], "DMCS_HEADER_READY")

        # these are currently being sent, but will be deprecated soon
        self.assertEqual(msg["FILENAME"], self.url)
        self.assertEqual(msg["IMAGE_ID"], self.id)

        # these are new
        self.assertEqual(msg["byteSize"], self.byte_size)
        self.assertEqual(msg["checkSum"], self.check_sum)
        self.assertEqual(msg["generator"], self.generator)
        self.assertEqual(msg["mimeType"], self.mime_type)
        self.assertEqual(msg["url"], self.url)
        self.assertEqual(msg["version"], self.version)
        self.assertEqual(msg["id"], self.id)
        self.assertEqual(msg["priority"], self.priority)


if __name__ == "__main__":
    unittest.main()
