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

import os
import unittest
from lsst.ctrl.iip.ocs.proxies.DeviceProxy import DeviceProxy
from lsst.ctrl.iip.ocs.messages.ATArchiverMessages import ATArchiverMessages


class test_data:
    def __init__(self):
        self.settingsToApply = None


class DeviceProxyTestCase(unittest.TestCase):
    def setUp(self):
        rootdir = os.environ["CTRL_IIP_DIR"]
        path = os.path.join(rootdir, "tests", "test_config")
        os.environ["IIP_CONFIG_DIR"] = path
        self.messages = ATArchiverMessages()
        self.deviceProxy = DeviceProxy("ATArchiver", "AT", self.messages, False, 0)

    def test_ack_commands(self):

        commands = self.messages.get_commands()
        for command in commands:
            method = self.deviceProxy.get_ack_command("%s_ACK" % command)
            self.assertTrue(method.__name__, "ackCommand_%s" % command)

    def test_log_events(self):
        log_events = self.messages.get_log_events()
        for log_event in log_events:
            method = self.deviceProxy.get_log_event_method(log_event)
            self.assertTrue(method.__name__, "logEvent_%s" % log_event)

    def test_build_abort_msg(self):
        command = "abort"
        cmd_id = 23
        ack_id = "ack_id"
        data = None
        d = self.deviceProxy.build_msg(command, cmd_id, ack_id, data)

        self.assertTrue(d['MSG_TYPE'], command)
        self.assertTrue(d['DEVICE'], self.deviceProxy.get_abbreviation())
        self.assertTrue(d['CMD_ID'], cmd_id)
        self.assertTrue(d['ACK_ID'], ack_id)
        self.assertFalse('CFG_KEY' in d)

    def test_build_start_msg(self):
        command = "start"
        cmd_id = 23
        ack_id = "ack_id"
        settings_to_apply = "foo, bar, baz"

        data = test_data()
        data.settingsToApply = settings_to_apply

        d = self.deviceProxy.build_msg(command, cmd_id, ack_id, data)

        self.assertTrue(d['MSG_TYPE'], command)
        self.assertTrue(d['DEVICE'], self.deviceProxy.get_abbreviation())
        self.assertTrue(d['CMD_ID'], cmd_id)
        self.assertTrue(d['ACK_ID'], ack_id)
        self.assertTrue(d['CFG_KEY'], settings_to_apply)

    def test_build_bookkeeping_msg(self):
        msg_type = 'BOOK_KEEPING'
        command = 'abort'
        ack_id = 'ack_id'
        checkbox = 'false'
        cmd_id = 12
        device = 'AT'

        d = self.deviceProxy.build_bookkeeping_msg(command, cmd_id, ack_id)

        self.assertTrue(d['MSG_TYPE'], msg_type)
        self.assertTrue(d['SUB_TYPE'], command)
        self.assertTrue(d['ACK_ID'], ack_id)
        self.assertTrue(d['CHECKBOX'], checkbox)
        self.assertTrue(d['CMD_ID'], str(cmd_id))
        self.assertTrue(d['DEVICE'], device)

    def test_build_summary_state_object(self):
        state = 'DISABLE'

        data = self.deviceProxy.create_object("logevent", "summaryState")

        msg = {'CURRENT_STATE': state}

        obj = self.deviceProxy.build_summaryState_object(data, msg)

        self.assertEqual(obj.summaryState, self.deviceProxy.get_sal_summary_state(state))
        self.assertEqual(obj.priority, 0)

        self.assertIsNone(self.deviceProxy.get_sal_summary_state('foobar'))

    def test_next_timed_ack_id(self):
        val = self.deviceProxy.next_ack_id+1
        command = 'ENABLE'

        retval = self.deviceProxy.get_next_timed_ack_id(command)

        self.assertEqual(retval, "%s_%06d" % (command, val))


if __name__ == "__main__":
    unittest.main()
