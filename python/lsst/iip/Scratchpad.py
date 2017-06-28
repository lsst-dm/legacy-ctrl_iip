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
        if job_number in list(self._pad.keys()): 
       	    self._pad[job_number][kee] = val 
        else: 
            self._pad[job_number] = {} 
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



