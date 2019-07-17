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
from lsst.ctrl.iip.ocs.messages.Messages import Messages


class DefaultMessages(Messages):
    """Default commands and log_events
    """
    def __init__(self):
        super().__init__()
        self.commands = ['enable', 'start', 'disable', 'enterControl', 'exitControl', 'standby', 'abort']

        self.log_events = ["summaryState", "settingVersions", "errorCode", "appliedSettingsMatchStart",
                           "settingsApplied"]

        self.translation_table = { 'enable': 'ENABLE',
                                   'start': 'START',
                                   'disable': 'DISABLE',
                                   'enterControl': 'ENTER_CONTROL',
                                   'exitControl': 'EXIT_CONTROL',
                                   'standby': 'STANDBY',
                                   'abort': 'ABORT' }



    def translate(self, command):
        return self.translation_table[command]

    def build_settingVersions_object(self, data, msg):
        """Build settingVersions SAL message object
        @param data: settingVersions SAL structure
        @param msg: message from DMCS
        @return settingVersions SAL structure with data
        """
        data.recommendedSettingsVersion = msg["CFG_KEY"]
        data.priority = 0
        return data

    def build_errorCode_object(self, data, msg):
        """Build errorCode SAL message object
        @param data: errorCode SAL structure
        @param msg: message from DMCS
        @return errorCode SAL structure with data
        """
        data.errorCode = msg["ERROR_CODE"]
        data.priority = 0
        return data

    def build_appliedSettingsMatchStart_object(self, data, msg):
        """Build appliedSettingsMatchStart SAL message object
        @param data: appliedSettingsMatchStart SAL structure
        @param msg: message from DMCS
        @return appliedSettingsMatchStart SAL structure with data
        """
        data.appliedSettingsMatchStartIsTrue = msg["APPLIED"]
        data.priority = 0
        return data

    def build_processingStatus_object(self, data, msg):
        """Build processingStatus SAL message object
        @param data: processingStatus SAL structure
        @param msg: message from DMCS
        @return processingStatus SAL structure with data
        """
        data.statusCode = msg["STATUS_CODE"]
        data.description = msg["DESCRIPTION"]
        data.priority = 0
        return data

    def build_settingsApplied_object(self, data, msg):
        """Build settingsApplied SAL message object
        @param data: settingsApplied SAL structure
        @param msg: message from DMCS
        @return settingsApplied SAL structure with data
        """
        data.settings = msg["SETTINGS"]
        data.tsSALVersion = msg["TS_SAL_VERSION"]
        data.tsXMLVersion = msg["TS_XML_VERSION"]
        data.l1dmRepoTag = msg["L1_DM_REPO_TAG"]
        return data
