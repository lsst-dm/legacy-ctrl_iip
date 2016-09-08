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
        tmp_dict = {}
        tmp_dict[kee] = val
        self._pad[job_number] = tmp_dict



    def set_job_transfer_params(self, job_number, params):
        self._pad[job_number][TRANSFER_PARAMS] = params
