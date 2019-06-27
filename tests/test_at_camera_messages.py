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
from lsst.ctrl.iip.ocs.messages.ATCameraMessages import ATCameraMessages
import SALPY_ATCamera


class ATCameraMessagesTestCase(unittest.TestCase):

    def setUp(self):
        self.camera_messages = ATCameraMessages()
        self.expected_events = ["startIntegration", "endReadout"]
        self.image_name = "image name"
        self.image_index = 12
        self.image_sequence_name = "sequence name"
        self.images_in_sequence = 1
        self.time_stamp = 1564858800.0
        self.exposure_time = 1564858800.1
        self.priority = 10

    def test_commands(self):
        commands = self.camera_messages.get_commands()
        self.assertEqual(len(commands), 0)

    def test_log_events(self):
        log_events = self.camera_messages.get_log_events()
        self.assertEqual(len(log_events), 0)

    def test_events(self):

        events = self.camera_messages.get_events()
        self.assertEqual(len(self.expected_events), len(events))

        for expected in self.expected_events:
            self.assertTrue(expected in events)

    def test_startIntegration_message(self):

        data = SALPY_ATCamera.ATCamera_logevent_startIntegrationC()
        data.imageName = self.image_name
        data.imageIndex = self.image_index
        data.imageSequenceName = self.image_sequence_name
        data.imagesInSequence = self.images_in_sequence
        data.timeStamp = self.time_stamp
        data.exposureTime = self.exposure_time
        data.priority = self.priority

        msg = self.camera_messages.build_startIntegration_message(data)

        self.assertEqual(msg["MSG_TYPE"], "DMCS_AT_START_INTEGRATION")
        self._check_equal(msg)

    def test_endReadout_message(self):

        data = SALPY_ATCamera.ATCamera_logevent_endReadoutC()
        data.imageName = self.image_name
        data.imageIndex = self.image_index
        data.imageSequenceName = self.image_sequence_name
        data.imagesInSequence = self.images_in_sequence
        data.timeStamp = self.time_stamp
        data.exposureTime = self.exposure_time
        data.priority = self.priority

        msg = self.camera_messages.build_endReadout_message(data)

        self.assertEqual(msg["MSG_TYPE"], "DMCS_AT_END_READOUT")
        self._check_equal(msg)

    def _check_equal(self, msg):
        # these are currently being sent, but will be deprecated soon
        self.assertEqual(msg["IMAGE_ID"], self.image_name)
        self.assertEqual(msg["IMAGE_INDEX"], self.image_index)
        self.assertEqual(msg["IMAGE_SEQUENCE_NAME"], self.image_sequence_name)
        self.assertEqual(msg["IMAGES_IN_SEQUENCE"], self.images_in_sequence)

        # these are new
        self.assertEqual(msg["imageName"], self.image_name)
        self.assertEqual(msg["imageIndex"], self.image_index)
        self.assertEqual(msg["imageSequenceName"], self.image_sequence_name)
        self.assertEqual(msg["imagesInSequence"], self.images_in_sequence)
        self.assertEqual(msg["timeStamp"], self.time_stamp)
        self.assertEqual(msg["exposureTime"], self.exposure_time)
        self.assertEqual(msg["priority"], self.priority)


if __name__ == "__main__":
    unittest.main()
