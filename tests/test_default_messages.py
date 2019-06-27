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
import importlib
import unittest
from lsst.ctrl.iip.ocs.messages.DefaultMessages import DefaultMessages


class MessagesTestCase(unittest.TestCase):

    def setUp(self):
        self.devices = ["ATArchiver", "EFD", "MTArchiver", "PromptProcessing", "CatchupArchiver"]
        self.default = DefaultMessages()

    def test_commands(self):
        commands = self.default.get_commands()
        expected_commands = ['enable', 'start', 'disable', 'enterControl', 'exitControl', 'standby', 'abort']

        self.assertTrue(len(commands), len(expected_commands))
        for expected in expected_commands:
            self.assertTrue(expected in commands)

    def test_log_events(self):
        log_events = self.default.get_log_events()
        expected_log_events = ["summaryState", "settingVersions", "errorCode", "appliedSettingsMatchStart",
                               "settingsApplied"]

        self.assertTrue(len(log_events), len(expected_log_events))
        for expected in expected_log_events:
            self.assertTrue(expected in log_events)

    def test_settingVersions_objects(self):
        for device in self.devices:
            self._test_settingVersions(device)

    def _test_settingVersions(self, device):
        config_key = "config key"

        msg = {}
        msg["CFG_KEY"] = config_key

        settingVersions = self.get_logevent_obj(device, "settingVersions")

        obj = self.default.build_settingVersions_object(settingVersions, msg)

        self.assertEqual(obj.recommendedSettingsVersion, config_key)
        self.assertEqual(obj.priority, 0)

    def test_errorCode_objects(self):
        for device in self.devices:
            self._test_errorCode(device)

    def _test_errorCode(self, device):
        error_code = 8675309
        msg = {}
        msg["ERROR_CODE"] = error_code

        errorCode = self.get_logevent_obj(device, "errorCode")

        obj = self.default.build_errorCode_object(errorCode, msg)
        self.assertEqual(obj.errorCode, error_code)
        self.assertEqual(obj.priority, 0)

    def test_appliedSettingsMatchStart_objects(self):
        for device in self.devices:
            self._test_appliedSettingsMatchStart(device)

    def _test_appliedSettingsMatchStart(self, device):
        msg = {}
        msg["APPLIED"] = True

        appliedSettingsMatchStart = self.get_logevent_obj(device, "appliedSettingsMatchStart")
        obj = self.default.build_appliedSettingsMatchStart_object(appliedSettingsMatchStart, msg)
        self.assertTrue(obj.appliedSettingsMatchStartIsTrue)
        self.assertEqual(obj.priority, 0)

        msg["APPLIED"] = False
        appliedSettingsMatchStart = self.get_logevent_obj(device, "appliedSettingsMatchStart")
        obj = self.default.build_appliedSettingsMatchStart_object(appliedSettingsMatchStart, msg)
        self.assertFalse(obj.appliedSettingsMatchStartIsTrue)
        self.assertEqual(obj.priority, 0)

    def test_processingStatus_objects(self):
        devices = ["ATArchiver"]
        for device in devices:
            self._test_processingStatus(device)

    def _test_processingStatus(self, device):
        msg = {}
        status_code = 987
        desc = "Fancy description here"
        msg["STATUS_CODE"] = status_code
        msg["DESCRIPTION"] = desc

        processingStatus = self.get_logevent_obj(device, "processingStatus")
        obj = self.default.build_processingStatus_object(processingStatus, msg)

        self.assertEqual(obj.statusCode, status_code)
        self.assertEqual(obj.description, desc)
        self.assertEqual(obj.priority, 0)

    def test_settingsApplied_objects(self):
        devices = ["ATArchiver", "MTArchiver", "PromptProcessing", "CatchupArchiver"]
        for device in devices:
            self._test_settingsApplied(device)

    def _test_settingsApplied(self, device):
        msg = {}
        settings = "foo,bar,baz"
        sal_version = "3.10"
        xml_version = "3.45"
        repo_tag = "123456789012"

        msg["SETTINGS"] = settings
        msg["TS_SAL_VERSION"] = sal_version
        msg["TS_XML_VERSION"] = xml_version
        msg["L1_DM_REPO_TAG"] = repo_tag

        settingsApplied = self.get_logevent_obj(device, "settingsApplied")
        obj = self.default.build_settingsApplied_object(settingsApplied, msg)

        self.assertEqual(obj.settings, settings)
        self.assertEqual(obj.tsSALVersion, sal_version)
        self.assertEqual(obj.tsXMLVersion, xml_version)
        self.assertEqual(obj.l1dmRepoTag, repo_tag)

    def get_logevent_obj(self, device, logevent_name):
        module = importlib.import_module("SALPY_%s" % device)
        obj = getattr(module, "%s_logevent_%sC" % (device, logevent_name))
        return obj


if __name__ == "__main__":
    unittest.main()
