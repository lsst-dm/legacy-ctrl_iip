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

import argparse
import importlib
import os
import sys

class Commander:
    """Issues commands to devices
    """
    def __init__(self, device_name, debugLevel, timeout):
        self.device_name = device_name

        self.module = importlib.import_module(f"SALPY_{self.device_name}")
        class_ = getattr(self.module, f"SAL_{self.device_name}")
        self.mgr = class_()
        self.mgr.setDebugLevel(debugLevel)

        self.timeout = timeout

    def createDataObject(self, command):
        """Build a command data structure
        @param command: specifies the correct command data structure to retrieve
        @return command data object
        """
        class_ = getattr(self.module, f"{self.device_name}_command_{command}C")
        data = class_()
        return data

    def getCommandMethod(self, command):
        """Retrieve the specified command method
        @param command: specifies the correct issueCommand to retrieve
        @return issue method
        """
        issue_command = getattr(self.mgr, f"issueCommand_{command}")
        return issue_command

    def getCompletionMethod(self, command):
        """Retrieve the specified waitForCompletion method
        @param command: specifies the correct waitForCompletion method
        @return waitForCompletion method
        """
        completion_command = getattr(self.mgr, f"waitForCompletion_{command}")
        return completion_command

    def executeCommand(self, command, settings):
        """Execute the command
        @param command: the command to send
        @param settings: optional settings to use
        """

        data = self.createDataObject(command)
        self.mgr.salCommand(f"{self.device_name}_command_{command}")
        data.device = ""
        data.property = ""
        data.action = ""
        if settings is None:
            data.value = 0
        else:
            data.settingsToApply = settings

        issue_command = self.getCommandMethod(command)
        completion_command = self.getCompletionMethod(command)

        cmdId = issue_command(data)
        status = completion_command(cmdId, self.timeout)

        return status

    def shutdown(self):
        """shutdown SAL
        """
        self.mgr.salShutdown()


if __name__ == "__main__":

    name = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(prog=name, description="Send SAL commands to devices")
    parser.add_argument("-D", "--device", type=str, dest="device", required=True,
                        help="component to which the command will be sent")
    parser.add_argument("-d", "--debug", type=int, choices=range(0,9), dest="debugLevel", default=0,
                        help="debug level output")
    parser.add_argument("-t", "--timeout", type=int, dest="timeout", default=10, help="command timeout")

    subparsers = parser.add_subparsers(dest="command")

    start_parser = subparsers.add_parser('start')
    start_parser.add_argument('-s', '--settings', dest="settings", required=True, help="setting to apply")

    cmds = ['enable', 'disable', 'enterControl','exitControl', 'standby', 'abort', 'resetFromFault']
    for x in cmds:
        p = subparsers.add_parser(x)

    args = parser.parse_args()

    settings = None
    if args.command == "start":
        settings = args.settings

    cmdr = Commander(args.device, args.debugLevel, args.timeout)
    status = cmdr.executeCommand(args.command, settings)
    cmdr.mgr.salShutdown()

    # SAL returns negative values on error; linux expects return values to be positive on program exit,
    # and generally between 0 and 127. We return "1" here to tell that something went wrong, so it can
    # be captured in shell scripts
    if status < 0:
        sys.exit(1)
    sys.exit(0)
