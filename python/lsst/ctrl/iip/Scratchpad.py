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

from toolsmod import get_timestamp
from const import *
import yaml
import os
import sys
import logging
import time
import pika
from SimplePublisher import SimplePublisher


class Scratchpad:
    REPORTS_PUBLISH = "reports_publish"

    def __init__(self, broker_url):
        self._name = 'scratchpad'
        self._passwd = 'scratchpad'
        self._pad = {}
        self._broker_url = broker_url
        self._publisher = SimplePublisher(self._broker_url)



    def set_job_value(self, job_number, kee, val):
        #tmp_dict = {}
        #tmp_dict[kee] = val
        self._pad[job_number][kee] = val 

    def get_job_value(self, job_number, kee):
        return self._pad[job_number]['XFER_PARAMS'][kee]

    def set_job_transfer_params(self, job_number, params):
        tmp_dict = {}
        tmp_dict['XFER_PARAMS'] = params
        self._pad[job_number] = tmp_dict

    def set_job_state(self, job_number, state):
        self._pad[job_number]['STATE'] = state 

    def keys(self):
        return list(self._pad.keys())



