###############################################################################
###############################################################################
## Copyright 2000-2018 The Board of Trustees of the University of Illinois.
## All rights reserved.
##
## Developed by:
##
##   LSST Image Ingest and Distribution Team
##   National Center for Supercomputing Applications
##   University of Illinois
##   http://www.ncsa.illinois.edu/enabling/data/lsst
##
## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the
## "Software"), to deal with the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish,
## distribute, sublicense, and/or sell copies of the Software, and to
## permit persons to whom the Software is furnished to do so, subject to
## the following conditions:
##
##   Redistributions of source code must retain the above copyright
##   notice, this list of conditions and the following disclaimers.
##
##   Redistributions in binary form must reproduce the above copyright
##   notice, this list of conditions and the following disclaimers in the
##   documentation and/or other materials provided with the distribution.
##
##   Neither the names of the National Center for Supercomputing
##   Applications, the University of Illinois, nor the names of its
##   contributors may be used to endorse or promote products derived from
##   this Software without specific prior written permission.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
## IN NO EVENT SHALL THE CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR
## ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
## CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
## WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH THE SOFTWARE.



import pika
import os
import os.path
import hashlib
import yaml
import zlib
import string
from subprocess import call
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from ThreadManager import ThreadManager 
from const import *
import toolsmod  
from toolsmod import *
from IncrScoreboard import IncrScoreboard
import _thread
import logging
import threading
import datetime


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class ArchiveController:

    ARCHIVE_CTRL_PUBLISH = "archive_ctrl_publish"
    ARCHIVE_CTRL_CONSUME = "archive_ctrl_consume"
    AR_ACK_PUBLISH = "ar_foreman_ack_publish"
    AT_ACK_PUBLISH = "at_foreman_ack_publish"
    AUDIT_CONSUME = "audit_consume"
    ERROR_CODE_PREFIX = '54'
    YAML = 'YAML'



    def __init__(self, filename=None):
        self._session_id = None
        self._name = "ARCHIVE_CTRL"
        self._config_file = 'L1SystemCfg.yaml'
        if filename != None:
            self._config_file = filename

        cdm = toolsmod.intake_yaml_file(self._config_file)

        try:
            self._archive_name = cdm[ROOT]['ARCHIVE_BROKER_NAME'] 
            self._archive_passwd = cdm[ROOT]['ARCHIVE_BROKER_PASSWD']

            self._archive_pub_name = cdm[ROOT]['ARCHIVE_BROKER_PUB_NAME'] 
            self._archive_pub_passwd = cdm[ROOT]['ARCHIVE_BROKER_PUB_PASSWD']

            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            self.incr_db_instance = cdm[ROOT]['SCOREBOARDS']['ARC_CTRL_RCPT_SCBD']

            # Root dir of where to put files
            self._archive_xfer_root = cdm[ROOT]['ARCHIVE']['ARCHIVE_XFER_ROOT']
            self._archive_ar_xfer_root = cdm[ROOT]['ARCHIVE']['ARCHIVE_AR_XFER_ROOT']
            self._archive_at_xfer_root = cdm[ROOT]['ARCHIVE']['ARCHIVE_AT_XFER_ROOT']

            if cdm[ROOT]['ARCHIVE']['CHECKSUM_ENABLED'] == 'yes':
                self.CHECKSUM_ENABLED = True
                if cdm[ROOT]['ARCHIVE']['CHECKSUM_TYPE'] == 'MD5':
                    self.CHECKSUM_TYPE = 'MD5'
                elif cdm[ROOT]['ARCHIVE']['CHECKSUM_TYPE'] == 'CRC32':
                    self.CHECKSUM_TYPE = 'CRC32'
                else:
                    self.CHECKSUM_ENABLED = False # if bad type, turn off csum's
            else:
                self.CHECKSUM_ENABLED = False
        except KeyError as e:
            LOGGER.critical('Key Error exception thrown when attempting to read L1 cfg file.')
            LOGGER.critical('No other choice but to bail out.')
            raise L1Error(e)

        os.makedirs(os.path.dirname(self._archive_xfer_root), exist_ok=True)
        os.makedirs(os.path.dirname(self._archive_ar_xfer_root), exist_ok=True)
        os.makedirs(os.path.dirname(self._archive_at_xfer_root), exist_ok=True)

        self._base_msg_format = self.YAML

        if 'BASE_MSG_FORMAT' in cdm[ROOT]:
            self._base_msg_format = cdm[ROOT][BASE_MSG_FORMAT]

        self._base_broker_url = "amqp://" + self._archive_name + ":" + \
                                 self._archive_passwd + "@" + str(self._base_broker_addr)

        self._pub_base_broker_url = "amqp://" + self._archive_pub_name + ":" + \
                                 self._archive_pub_passwd + "@" + str(self._base_broker_addr)

        LOGGER.info('Building _base_broker_url connection string for Archive Controller.' + \
                    ' Result is %s' % self._base_broker_url)

        self._msg_actions = { 'ARCHIVE_HEALTH_CHECK': self.process_health_check,
                              'NEW_AR_ARCHIVE_ITEM': self.process_new_ar_archive_item,
                              'NEW_AT_ARCHIVE_ITEM': self.process_new_at_archive_item,
                              'AR_ITEMS_XFERD': self.process_ar_transfer_complete,
                              'AT_ITEMS_XFERD': self.process_at_transfer_complete }

        # Set up Incr Scbd...
        try:
            LOGGER.info('Setting up Archive Incr Scoreboard')
            self.INCR_SCBD = IncrScoreboard('ARC_CTRL_RCPT_SCBD', self.incr_db_instance)
        except L1RedisError as e:
            LOGGER.error("DMCS unable to complete setup_scoreboards - " + \
                         "No Redis connect: %s" % e.args)
            print("DMCS unable to complete setup_scoreboards - No Redis connection: %s" % e.args)
            ### FIXX - send Fault Instead...
            sys.exit(self.ERROR_CODE_PREFIX + 12)

        self.setup_consumer()
        self.setup_publisher()


    def setup_consumer(self):
        LOGGER.info('Setting up archive consumers on %s', self._base_broker_url)
        LOGGER.info('Running start_new_thread for archive consumer')

        self.shutdown_event = threading.Event() 
        self.shutdown_event.clear() 

        kws = {}
        md = {}
        md['amqp_url'] = self._base_broker_url
        md['name'] = 'Thread-ar_ctrl_consume'
        md['queue'] = self.ARCHIVE_CTRL_CONSUME
        md['callback'] = self.on_archive_message
        md['format'] = "YAML"
        md['test_val'] = None
        kws[md['name']] = md

        self.thread_manager = ThreadManager('thread-manager', kws, self.shutdown_event)
        self.thread_manager.start()


    def setup_publisher(self):
        LOGGER.info('Setting up Archive publisher on %s using %s',\
                     self._pub_base_broker_url, self._base_msg_format)
        self._archive_publisher = SimplePublisher(self._pub_base_broker_url, self._base_msg_format)
        #self._audit_publisher = SimplePublisher(self._base_broker_url, self._base_msg_format)



    def on_archive_message(self, ch, method, properties, msg_dict):
        ch.basic_ack(method.delivery_tag)
        LOGGER.info('Message from Archive callback message body is: %s', str(msg_dict))
        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)


    def process_health_check(self, params):
        """Input 'params' for this method is a dict made up of:
           :param str 'MESSAGE_TYPE' value  is 'ARCHIVE_HEALTH_CHECK'
           :param str 'ACK_ID' value  is an alphanumeric string, with 
               the numeric part a momotonically increasing sequence. 
               This value is passed back to the foreman and used to keep 
               track of acknowledgement time.
           :param str 'SESSION_ID' Might be useful for the controller to 
               generate a target location for new items to be archived?
        """
        #self.send_audit_message("received_", params)
        self.send_health_ack_response("ARCHIVE_HEALTH_CHECK_ACK", params)
        

    def process_new_ar_archive_item(self, params):
        #self.send_audit_message("received_", params)
        final_target_dir = self.construct_send_target_dir(self._archive_ar_xfer_root)
        self.send_new_item_ack(final_target_dir, params)


    def process_new_at_archive_item(self, params):
        #self.send_audit_message("received_", params)
        final_target_dir = self.construct_send_target_dir(self._archive_at_xfer_root)
        self.send_new_item_ack(final_target_dir, params)


    def process_ar_transfer_complete(self, params):
        transfer_results = {}
        ccds = params['RESULT_SET']['CCD_LIST']
        fnames = params['RESULT_SET']['FILENAME_LIST']
        csums = params['RESULT_SET']['CHECKSUM_LIST']
        num_ccds = len(ccds)
        transfer_results = {}
        RECEIPT_LIST = [] 
        for i in range(0, num_ccds):
            ccd = ccds[i]
            pathway = fnames[i]
            csum = csums[i]
            transfer_result = self.check_transferred_file(pathway, csum)
            if transfer_result == None:
                RECEIPT_LIST.append('0')
            else:
                RECEIPT_LIST.append(transfer_result) 
        transfer_results['CCD_LIST'] = ccds
        transfer_results['RECEIPT_LIST'] = RECEIPT_LIST
        self.send_transfer_complete_ack(transfer_results, params)


    def process_at_transfer_complete(self, params):
        transfer_results = {}
        ccds = params['RESULT_SET']['CCD_LIST']
        fnames = params['RESULT_SET']['FILENAME_LIST']
        csums = params['RESULT_SET']['CHECKSUM_LIST']
        num_ccds = len(ccds)
        transfer_results = {}
        RECEIPT_LIST = [] 
        for i in range(0, num_ccds):
            ccd = ccds[i]
            pathway = fnames[i]
            csum = csums[i]
            transfer_result = self.check_transferred_file(pathway, csum)
            if transfer_result == None:
                RECEIPT_LIST.append('0')
            else:
                RECEIPT_LIST.append(transfer_result) 
        transfer_results['CCD_LIST'] = ccds
        transfer_results['RECEIPT_LIST'] = RECEIPT_LIST
        self.send_transfer_complete_ack(transfer_results, params)


    def check_transferred_file(self, pathway, csum):
        if not os.path.isfile(pathway):
            return ('-1') # File doesn't exist

        if self.CHECKSUM_ENABLED == True:
            if self.CHECKSUM_TYPE == 'MD5':
                new_csum = self.calculate_md5(pathway)
                if new_csum != csum:
                    return ('0')
                else:
                    return self.next_receipt_number()

            if self.CHECKSUM_TYPE == 'CRC32':
                new_csum = self.calculate_crc32(pathway)
                if new_csum != csum:
                    return ('0')
                else:
                    return self.next_receipt_number()

        return self.next_receipt_number()


    def calculate_crc32(self, filename):
        new_crc32 = 0
        buffersize = 65536

        try:
            with open(filename, 'rb') as afile:
                buffr = afile.read(buffersize)
                crcvalue = 0
                while len(buffr) > 0:
                    crcvalue = zlib.crc32(buffr, crcvalue)
                    buffr = afile.read(buffersize)
        except IOError as e:
            LOGGER.critical("Unable to open file %s for CRC32 calculation. " + \
                            "Returning zero receipt value" % filename )
            return new_crc32

        new_crc32 = format(crcvalue & 0xFFFFFFFF, '08x').upper()
        LOGGER.debug("Returning newly calculated crc32 value: " % new_crc32)
        print("Returning newly calculated crc32 value: " % new_crc32)

        return new_crc32


    def calculate_md5(self, filename):
        new_md5 = 0
        try:
            with open(filename) as file_to_calc:
                data = file_to_calc.read()
                new_md5 = hashlib.md5(data).hexdigest()
        except IOError as e:
            LOGGER.critical("Unable to open file %s for MD5 calculation. " +\
                            "Returning zero receipt value" % filename)
            return new_md5

        LOGGER.debug("Returning newly calculated md5 value: " % new_md5)
        print("Returning newly calculated md5 value: " % new_md5)

        return new_md5


    def next_receipt_number(self):
        current_receipt = self.INCR_SCBD.get_next_receipt_id()
        return current_receipt


    def send_health_ack_response(self, type, params):
        try:
            ack_id = params.get("ACK_ID")
            self._current_session_id = params.get("SESSION_ID")
        except:
            if ack_id == None:
                LOGGER.info('%s failed, missing ACK_ID field', type)
                raise L1MessageError("Missing ACK_ID message param needed for send_ack_response")
            else:
                LOGGER.info('%s failed, missing SESSION_ID field', type)
                raise L1MessageError("Missing SESSION_ID param needed for send_ack_response")

        msg_params = {}
        msg_params[MSG_TYPE] = type
        msg_params[COMPONENT] = self._name
        msg_params[ACK_BOOL] = "TRUE"
        msg_params['ACK_ID'] = ack_id
        LOGGER.info('%s sent for ACK ID: %s', type, ack_id)
        self._archive_publisher.publish_message(self.ACK_PUBLISH, msg_params)


    def send_audit_message(self, prefix, params):
        audit_params = {}
        audit_params['SUB_TYPE'] = str(prefix) + str(params['MSG_TYPE']) + "_msg"
        audit_params['DATA_TYPE'] = self._name
        audit_params['TIME'] = get_epoch_timestamp()
        self._archive_publisher.publish_message(self.AUDIT_CONSUME, audit_params)



    def construct_send_target_dir(self, target_dir):
        today = datetime.datetime.now()
        day_string = today.date()

        final_target_dir = target_dir + "/" + str(day_string) + "/"

        if os.path.isdir(final_target_dir):
            pass
        else:
            os.mkdir(final_target_dir, 0o2776)

        return final_target_dir


    def send_new_item_ack(self, target_dir, params):
        ack_params = {}
        new_type = params[MSG_TYPE] + "_ACK"
        reply_queue = params[REPLY_QUEUE]
        ack_params[MSG_TYPE] = new_type
        ack_params['TARGET_DIR'] = target_dir
        ack_params['ACK_ID'] = params['ACK_ID']
        ack_params['JOB_NUM'] = params['JOB_NUM']
        ack_params['IMAGE_ID'] = params['IMAGE_ID']
        ack_params['COMPONENT'] = self._name
        ack_params['ACK_BOOL'] = True
        self._archive_publisher.publish_message(reply_queue, ack_params)


    def send_transfer_complete_ack(self, transfer_results, params):
        ack_params = {}
        keez = list(params.keys())
        for kee in keez:
            if kee == 'MSG_TYPE' or kee == 'CCD_LIST':
                continue
            ### XXX FIXME Dump loop and just pull the correct values from the input params
            ack_params[kee] = params[kee]

        
        ack_params['MSG_TYPE'] = 'AR_ITEMS_XFERD_ACK'
        ack_params['COMPONENT'] = self._name
        ack_params['ACK_ID'] = params['ACK_ID']
        ack_params['ACK_BOOL'] = True
        ack_params['RESULTS'] = transfer_results

        self._archive_publisher.publish_message(self.ACK_PUBLISH, ack_params)




def main():
    logging.basicConfig(filename='logs/BaseForeman.log', level=logging.INFO, format=LOG_FORMAT)
    a_c = ArchiveController()
    print("Beginning ArchiveController event loop...")
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        x = os.getpid()
        print("Killing PID: %s" % x)
        call(["kill","-9",str(x)])
        pass

    print("")
    print("Archive Controller Done.")



if __name__ == "__main__": main()
