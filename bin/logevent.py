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
import time

class Emitter:
    """Issues commands to devices
    """
    def __init__(self, device_name, debugLevel):
        self.device_name = device_name

        self.module = importlib.import_module(f"SALPY_{self.device_name}")
        class_ = getattr(self.module, f"SAL_{self.device_name}")
        self.mgr = class_()
        self.mgr.setDebugLevel(debugLevel)

    def createDataObject(self, logevent):
        """Build a logevent data structure
        @param logevent: specifies the correct logevent data structure to retrieve
        @return logevent data object
        """
        class_ = getattr(self.module, f"{self.device_name}_logevent_{logevent}C")
        data = class_()
        return data

    def _fill(self, data, args):
        data.imageSequenceName = args.imageSequenceName
        data.imagesInSequence = args.imagesInSequence
        data.imageName = args.imageName
        data.imageIndex = args.imageIndex
        data.timeStamp = args.timeStamp
        data.exposureTime = args.exposureTime
        data.priority = args.priority

    def issueStartIntegrationEvent(self, args):
        """Emit a startIntegration logevent
        @param args: data to fill in for startIntegration, as passed from command line
        """

        data = self.createDataObject("startIntegration")
        self.mgr.salCommand(f"ATCamera_logevent_startIntegration")
        self._fill(data, args)

        self.mgr.logEvent_startIntegration(data, args.priority)

    def issueEndReadoutEvent(self, args):
        """Emit a startIntegration logevent
        @param args: data to fill in for endReadout, as passed from command line
        """
        data = self.createDataObject("endReadout")
        self.mgr.salCommand(f"ATCamera_logevent_endReadout")
        self._fill(data, args)
        self.mgr.logEvent_endReadout(data, args.priority)

    def issueLargeFileObjectAvailableEvent(self, args):
        """Emit a largeFileObjectAvailable logevent
        @param args: data to fill in for largeFileObjectAvailable, as passed from command line
        """
        data = self.createDataObject('largeFileObjectAvailable')
        self.mgr.salCommand(f'EFD_logevent_largeFileObjectAvailable')

        data.byteSize = args.byteSize
        data.checkSum = args.checkSum
        data.generator = args.generator
        data.mimeType = args.mimeType
        data.url = args.url
        data.version = args.version
        data.id = args.id

        self.mgr.logEvent_largeFileObjectAvailable(data, args.priority)

    def shutdown(self):
        """shutdown SAL
        """
        self.mgr.salShutdown()


if __name__ == "__main__":

    name = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(prog=name, description="Send SAL logevents")
    parser.add_argument("-d", "--debug", type=int, choices=range(0,9), dest="debugLevel", default=0, help="debug level output")

    subparsers = parser.add_subparsers(dest="command")

    si_parser = subparsers.add_parser('startIntegration')
    si_parser.add_argument('-q', '--imageSequenceName', type=str, dest='imageSequenceName', required=True, help='image sequence Name')
    si_parser.add_argument('-s', '--imagesInSequence', type=int, dest='imagesInSequence', required=True, help='images in sequence')
    si_parser.add_argument('-n', '--imageName', type=str, dest='imageName', required=True, help='image name')
    si_parser.add_argument('-i', '--imageIndex', type=int, dest='imageIndex', required=True, help='image Index')
    si_parser.add_argument('-t', '--timeStamp', type=float, dest='timeStamp', required=True, help='time stamp')
    si_parser.add_argument('-e', '--exposureTime', type=float, dest='exposureTime', required=True, help='exposure time')
    si_parser.add_argument('-p', '--priority', type=int, dest='priority', required=True, help='priority')

    er_parser = subparsers.add_parser('endReadout')
    er_parser.add_argument('-q', '--imageSequenceName', type=str, dest='imageSequenceName', required=True, help='image sequence Name')
    er_parser.add_argument('-s', '--imagesInSequence', type=int, dest='imagesInSequence', required=True, help='images in sequence')
    er_parser.add_argument('-n', '--imageName', type=str, dest='imageName', required=True, help='image name')
    er_parser.add_argument('-i', '--imageIndex', type=int, dest='imageIndex', required=True, help='image Index')
    er_parser.add_argument('-t', '--timeStamp', type=float, dest='timeStamp', required=True, help='time stamp')
    er_parser.add_argument('-e', '--exposureTime', type=float, dest='exposureTime', required=True, help='exposure time')
    er_parser.add_argument('-p', '--priority', type=int, dest='priority', required=True, help='priority')


    efd_parser = subparsers.add_parser('largeFileObjectAvailable')
    efd_parser.add_argument('-b', '--byteSize', type=int, dest='byteSize', required=True, help='byte size')
    efd_parser.add_argument('-c', '--checkSum', type=str, dest='checkSum', required=True, help='checksum')
    efd_parser.add_argument('-g', '--generator', type=str, dest='generator', required=True, help='generator')
    efd_parser.add_argument('-m', '--mimeType', type=str, dest='mimeType', required=True, help='mime type')
    efd_parser.add_argument('-u', '--url', type=str, dest='url', required=True, help='url')
    efd_parser.add_argument('-v', '--version', type=float, dest='version', required=True, help='version')
    efd_parser.add_argument('-i', '--id', type=str, dest='id', required=True, help='id')
    efd_parser.add_argument('-p', '--priority', type=int, dest='priority', required=True, help='priority')

    args = parser.parse_args()

    emitter = None
    if args.command == "startIntegration":
        emitter = Emitter("ATCamera", args.debugLevel)
        emitter.issueStartIntegrationEvent(args)
    elif args.command == "endReadout":
        emitter = Emitter("ATCamera", args.debugLevel)
        emitter.issueEndReadoutEvent(args)
    elif args.command == "largeFileObjectAvailable":
        emitter = Emitter("EFD", args.debugLevel)
        emitter.issueLargeFileObjectAvailableEvent(args)
    else:
        print("You need to give a command...")
        sys.exit(0)
    time.sleep(1)
    emitter.shutdown()

    sys.exit(0)

