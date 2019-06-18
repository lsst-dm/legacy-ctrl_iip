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


class Messages:
    """Base class which keeps the types of commmands, events and log events a CSC acts on or issues.
    """

    def __init__(self):
        self.commands = []
        self.events = []
        self.log_events = []
        self.composers = []

    def get_commands(self):
        """Retrieve the list of registered commands
        """
        return self.commands

    def get_events(self):
        """Retrieve the list of registered events
        """
        return self.events

    def get_log_events(self):
        """Retrieve the list of registered log_events
        """
        return self.log_events

    def get_composer(self, name):
        """Retrieve a method which can be used to build a specific message type
        @returns message formatting method
        """
        composer = getattr(self, "build_%s_message" % name)
        return composer

    def get_command_acks(self):
        acks = []
        for command in self.commands:
            acks.append("%s_ACK" % command)
        return acks
