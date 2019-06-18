#!/usr/bin/env python3

# This file is part of ctrl_iip.
#
# Developed for the LSST Telescope and Site Systems.
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
import os
import sys
from lsst.ctrl.iip.ocs.OCSBridge import OCSBridge

name = os.path.basename(sys.argv[0])

parser = argparse.ArgumentParser(prog=name, description='''Serves as a translator between SAL and RabbitMQ''')

parser.add_argument("-k", "--local_ack", action="store_true", dest="local_ack", default=False,
                    help="acknowledge messages without pass through")

parser.add_argument("-d", "--debug", type=int, choices=range(0,9), dest="debug", default=0, help="debug level output")
parser.add_argument("-c", "--config", type=str, dest="config", default="L1SystemCfg.yaml", help="configuration to load from configuration directory")

args = parser.parse_args()

bridge = OCSBridge(args.config, args.local_ack, args.debug)

# register SIGINT signal for orderly shutdown
bridge.register_SIGINT_handler()

# Bridge now goes into an infinite loop, cycling through all the
# commands it can accept from the OCS for the registered CSCs.
bridge.listen_loop()
