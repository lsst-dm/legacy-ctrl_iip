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


class Action:
    """Holds the set of accept and ack methods for a device and command
    Parameters
    ----------
    device_name: `str`
        The name of the CSC
    message: `str`
        The message the CSC can respond to
    message_retriever: method
        The method of the CSC device to use to retrieve message
    ack_method: method
        The method of the CSC device to use to acknowledge message.
    """

    def __init__(self, device_name, message, message_retriever, ack_method=None):
        self.device_name = device_name
        self.message = message
        self.message_retriever = message_retriever
        self.ack_method = ack_method
