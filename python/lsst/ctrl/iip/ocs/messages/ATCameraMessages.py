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


class ATCameraMessages(Messages):
    """ATCamera Messages
    """
    def __init__(self):
        super().__init__()
        self.commands = []   # Do not respond to commmands
        self.log_events = []
        self.events = ["startIntegration", "endReadout"]

    def build_startIntegration_message(self, data):
        d = {}
        d['MSG_TYPE'] = "DMCS_AT_START_INTEGRATION"

        # these are the old names.  This will be removed when we can update the other
        # parts of the code that depend on these names.
        d['IMAGE_ID'] = data.imageName
        d['IMAGE_INDEX'] = data.imageIndex
        d['IMAGE_SEQUENCE_NAME'] = data.imageSequenceName
        d['IMAGES_IN_SEQUENCE'] = data.imagesInSequence

        # this is what we're transitioning to.
        d['imageName'] = data.imageName
        d['imageIndex'] = data.imageIndex
        d['imageSequenceName'] = data.imageSequenceName
        d['imagesInSequence'] = data.imagesInSequence
        d['timeStamp'] = data.timeStamp
        d['exposureTime'] = data.exposureTime
        d['priority'] = data.priority
        return d

    def build_endReadout_message(self, data):
        d = {}
        d['MSG_TYPE'] = "DMCS_AT_END_READOUT"

        # these are the old names.  This will be removed when we can update the other
        # parts of the code that depend on these names.
        d['IMAGE_ID'] = data.imageName
        d['IMAGE_INDEX'] = data.imageIndex
        d['IMAGE_SEQUENCE_NAME'] = data.imageSequenceName
        d['IMAGES_IN_SEQUENCE'] = data.imagesInSequence

        # this is what we're transitioning to.
        d['imageSequenceName'] = data.imageSequenceName
        d['imagesInSequence'] = data.imagesInSequence
        d['imageName'] = data.imageName
        d['imageIndex'] = data.imageIndex
        d['timeStamp'] = data.timeStamp
        d['exposureTime'] = data.exposureTime
        d['priority'] = data.priority

        return d
