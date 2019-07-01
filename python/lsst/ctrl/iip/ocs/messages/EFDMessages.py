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


class EFDMessages(Messages):
    """EFD additional messages
    """

    def __init__(self):
        super().__init__()
        self.commands = []   # Do not respond to commmands
        self.log_events = []  # Do not respon to log events
        self.events = ["largeFileObjectAvailable"]

    def build_largeFileObjectAvailable_message(self, data):
        d = {}

        device = data.generator
        if device == "ATHeaderService":
            d['MSG_TYPE'] = "DMCS_AT_HEADER_READY"
        else:
            d['MSG_TYPE'] = "DMCS_HEADER_READY"

        d['FILENAME'] = data.url
        d['IMAGE_ID'] = data.id

        d['byteSize'] = data.byteSize
        d['checkSum'] = data.checkSum
        d['generator'] = data.generator

        d['generator'] = data.generator
        d['mimeType'] = data.mimeType
        d['url'] = data.url
        d['version'] = data.version
        d['id'] = data.id
        d['priority'] = data.priority
        return d
