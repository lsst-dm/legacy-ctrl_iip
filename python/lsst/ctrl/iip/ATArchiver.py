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

import threading
import lsst.ctrl.iip.toolsmod as toolsmod
from lsst.ctrl.iip.toolsmod import get_timestamp
import logging
import pika
import redis
import yaml
import sys
import os
from copy import deepcopy
from pprint import pprint, pformat
import time
import signal
import datetime
from time import sleep
import threading
from threading import Lock
from lsst.ctrl.iip.const import *
from lsst.ctrl.iip.Scoreboard import Scoreboard
from lsst.ctrl.iip.Credentials import Credentials
from lsst.ctrl.iip.JobScoreboard import JobScoreboard
from lsst.ctrl.iip.AckScoreboard import AckScoreboard
from lsst.ctrl.iip.Consumer import Consumer
from lsst.ctrl.iip.AsyncPublisher import AsyncPublisher
from lsst.ctrl.iip.iip_base import iip_base

LOGGER = logging.getLogger(__name__)


class ATArchiver(iip_base):
    """ The Spec Device is a commandable device which coordinates the ingest of
        images from the telescope camera and then the transfer of those images to
        the base site archive storage.
        It receives jobs and divides and assigns the work to forwarders, records state and
        status change of forwarders, and sends messages accordingly.
    """
    COMPONENT_NAME = 'AUX_FOREMAN'
    COMPONENT = 'AUX_FOREMAN'
    DEVICE = 'AT'
    ARCHIVE = 'ARCHIVE'
    FWDR = 'FWDR'
    AT_FOREMAN_CONSUME = "at_foreman_consume"
    ARCHIVE_CTRL_PUBLISH = "archive_ctrl_publish"
    ARCHIVE_CTRL_CONSUME = "archive_ctrl_consume"
    AT_FOREMAN_ACK_PUBLISH = "at_foreman_ack_publish"
    DMCS_ACK_CONSUME = "dmcs_ack_consume"
    DMCS_FAULT_CONSUME = "dmcs_fault_consume"
    TELEMETRY_QUEUE = "telemetry_queue"
    START_INTEGRATION_XFER_PARAMS = {}
    ACK_QUEUE = []
    prp = toolsmod.prp
    DP = toolsmod.DP
    METRIX = toolsmod.METRIX
    RAFT_LIST = []
    RAFT_CCD_LIST = ['00']


    def __init__(self, filename):
        """ Create a new instance of the Spectrograph Device class.
            Instantiate the instance, raise assertion error if already instantiated.
            Extract config values from yaml file.
            Store handler methods for each message type.
            Set up base broker url, publishers, and scoreboards. Consumer threads
            are started within a Thread Manager object so that they can be monitored
            for health and shutdown/joined cleanly when the app exits.

            :params filename: configuration file

            :return: None.
        """
        super().__init__(filename)

        self.service_user = self.cred.getUser('service_user')
        self.service_passwd = self.cred.getPasswd('service_passwd')

        self.DP = False

        print('Extracting values from Config dictionary %s' % filename)
        cdm = self.extract_config_values(filename)

        logging_dir = cdm[ROOT].get('LOGGING_DIR', None)

        log_file = self.setupLogging(logging_dir, 'ATArchiver.log')
        print("Logs will be written to %s" % log_file)


        toolsmod.singleton(self)
        self._fwdr_state_dict = {}  # Used for ACK analysis...
        self._archive_ack = {}  # Used to determine archive response
        self._current_fwdr = None

        self.setup_fwdr_state_dict()
        if self._use_mutex:
            self.my_mutex_lock = threading.Lock()

        #self.purge_broker(cdm['ROOT']['QUEUE_PURGES'])



        self._msg_actions = { 'AT_START_INTEGRATION': self.process_at_start_integration,
                              'AT_NEW_SESSION': self.set_session,
                              'AT_FWDR_HEALTH_CHECK_ACK': self.process_health_check_ack,
                              'AT_FWDR_XFER_PARAMS_ACK': self.process_xfer_params_ack,
                              'AT_FWDR_END_READOUT_ACK': self.process_at_fwdr_end_readout_ack,
                              'AT_ITEMS_XFERD_ACK': self.process_at_items_xferd_ack,
                              'AT_HEADER_READY': self.process_header_ready_event,
                              'AT_FWDR_HEADER_READY_ACK': self.process_header_ready_ack,
                              'NEW_ARCHIVE_ITEM_ACK': self.process_ack, 
                              'NEW_AR_ARCHIVE_ITEM_ACK': self.process_ack, 
                              'NEW_AT_ARCHIVE_ITEM_ACK': self.process_new_at_item_ack, 
                              'AT_END_READOUT': self.process_at_end_readout }


        self._next_timed_ack_id = 0

        self.base_broker_url = "amqp://%s:%s@%s" % (self.service_user, self.service_passwd, self._base_broker_addr)

        self.pub_base_broker_url = "amqp://%s:%s@%s" % (self.service_user, self.service_passwd, self._base_broker_addr)



        self.setup_publishers()
        self.setup_forwarder_thread()


        LOGGER.info("Acquiring forwarder")
        self.wait_for_forwarder()

        LOGGER.info("Forwarder acquired")
        self.setup_consumer_threads()

    def setup_publishers(self):
        """ Set up base publisher with pub_base_broker_url by creating a new instance
            of AsyncPublisher clas

            :params: None.

            :return: None.
        """
        #LOGGER.info('Setting up ATArchiver publisher on %s using %s', self.pub_base_broker_url, self._base_msg_format)
        LOGGER.info('Setting up ATArchiver publisher')
        self.setup_unpaired_publisher(self.pub_base_broker_url, 'ATArchiver-publisher')


    def on_aux_foreman_message(self, ch, method, properties, body):
        """ Calls the appropriate AR message action handler according to message type.

            :params ch: Channel to message broker, unused unless testing.
            :params method: Delivery method from Pika, unused unless testing.
            :params properties: Properties from DMCS to AR Foreman callback message
                                body, unused unless testing.
            :params body: A dictionary that stores the message body.

            :return: None.
        """
        if self.DP:
            print('-->on_aux_foreman_message')
            print(ch)
            print(method)
            print(properties)
            print(body)
            print('<--')
        ch.basic_ack(delivery_tag=method.delivery_tag)
        msg_dict = body 
        if self.DP:
            print("Incoming message to on_aux_foreman_message is: ")
            self.prp.pprint(msg_dict)

        LOGGER.info('on_aux_foreman_message: Msg received in ATArchiver message callback')
        LOGGER.debug('Message from DMCS to ATArchiver callback message body is: %s', pformat(str(msg_dict)))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def on_archive_message(self, ch, method, properties, body):
        """ Calls the appropriate AR message action handler according to message type.

            :params ch: Channel to message broker, unused unless testing.
            :params method: Delivery method from Pika, unused unless testing.
            :params properties: Properties from AR CTRL callback message body,
                                unused unless testing.
            :params body: A dictionary that stores the message body.

            :return: None.
        """
        if self.DP:
            print('-->on_archive_message')
            print(ch)
            print(method)
            print(properties)
            print(body)
            print('<--')
        ch.basic_ack(method.delivery_tag)
        msg_dict = body 
        LOGGER.info('In AT ARCHIVE CTRL message callback: RECEIVING MESSAGE')
        LOGGER.debug('Message from AT ARCHIVE CTRL callback message body is: %s', pformat(str(body)))

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)

    def on_ack_message(self, ch, method, properties, body):
        """ Calls the appropriate AR message action handler according to message type.

            :params ch: Channel to message broker, unused unless testing.
            :params method: Delivery method from Pika, unused unless testing.
            :params properties: Properties from ACK callback message body, unused
                                unless testing.
            :params body: A dictionary that stores the message body.

            :return: None.
        """
        if self.DP:
            print('-->on_ack_message')
            print(ch)
            print(method)
            print(properties)
            print(body)
            print('<--')
        ch.basic_ack(method.delivery_tag) 
        msg_dict = body 
        LOGGER.info('In ACK message callback: RECEIVING ACK MESSAGE')
        LOGGER.info('Message in an ACK callback message body is: %s', pformat(str(msg_dict)))

        if self.DP:
            print("\n\nIn ATArchiver on_ack_message - receiving this message: %s" % body)


        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)
    

    def do_health_check(self):
        health_check_ack_id = self.get_next_timed_ack_id('AT_FWDR_HEALTH_CHECK_ACK')
        self.clear_fwdr_state()
        num_fwdrs_checked = self.do_fwdr_health_check(health_check_ack_id)

        # Give fwdrs enough time to respond...
        ## FIX - Note: Incorporate way for simple_prog timer to do health checks.
        self.ack_timer(2.0)
        #fwdr_res = self.simple_progressive_ack_timer(self.FWDR, 4.0)


        if self.set_current_fwdr() == False:
            return False
        return True


    def process_at_start_integration(self, params):
        # When this method is invoked, the following must happen:
        #    1) Health check all forwarders
        #    2) Divide work and generate dict of forwarders and which rafts/ccds they are fetching
        #    3) Inform each forwarder which rafts they are responsible for
        # receive new job_number and image_id; session and visit are current
        # and deep copy it with some additions such as session and visit
        # These next three lines must have WFS and Guide sensor info added
        LOGGER.info('In top of Start_Int message handler: RECEIVING START_INT MESSAGE')
        LOGGER.info('Message from Start_Int handler message body is: %s', pformat(str(params)))

        start_int_ack_id = params[ACK_ID]
        session_id = params['SESSION_ID']
        job_number = params['JOB_NUM']
        image_id = params['IMAGE_ID']

        if self.DP: print("Incoming AUX AT_Start Int msg")
        # next, run health check
        self.ACK_QUEUE = {}
        

        if self.do_health_check() == False:
            LOGGER.critical("No health check response from ANY fwdr. Setting FAULT state, 5751")
            desc = "No health check response from ANY fwdr"
            self.send_fault_state_event("5751", desc, 'FAULT', 'FORWARDER' ) # error code for 'no health check response any fwdrs'
            return

        # Add archive check when necessary...
        if self.use_archive_ctrl == False:
            pass
        self.clear_archive_ack()

        # send new_archive_item msg to archive controller
        start_int_params = {}
        ac_timed_ack = self.get_next_timed_ack_id('AUX_CTRL_NEW_ITEM')
        start_int_params[MSG_TYPE] = 'NEW_AT_ARCHIVE_ITEM'
        start_int_params['ACK_ID'] = ac_timed_ack
        start_int_params['JOB_NUM'] = job_number
        start_int_params['SESSION_ID'] = session_id
        start_int_params['IMAGE_ID'] = image_id
        start_int_params['REPLY_QUEUE'] = self.AT_FOREMAN_ACK_PUBLISH
        self.publish_message(self.ARCHIVE_CTRL_CONSUME, start_int_params)

        ar_response = self.simple_progressive_ack_timer(self.ARCHIVE, 4.0)

        if ar_response == False:
            description = ("Non-Fatal Error - No NEW_AT_ARCHIVE_ITEM response from ArchiveCtrl." + \
                           "Using default Archive Dir location from CFG file: %s" \
                            % self.archive_xfer_root)
            LOGGER.critical(description)
            self.send_telemetry("4451", description) 
            target_dir = self.archive_xfer_root 
 
        else:
            target_dir = self._archive_ack['TARGET_DIR']
          
 
        xfer_params_ack_id = self.get_next_timed_ack_id("AT_FWDR_XFER_PARAMS_ACK") 

        fwdr_new_target_params = {} 
        fwdr_new_target_params['XFER_PARAMS'] = {}
        fwdr_new_target_params[MSG_TYPE] = 'AT_FWDR_XFER_PARAMS'
        fwdr_new_target_params[SESSION_ID] = params['SESSION_ID']
        fwdr_new_target_params[IMAGE_ID] = image_id
        fwdr_new_target_params['DEVICE'] = self.DEVICE
        fwdr_new_target_params[JOB_NUM] = params[JOB_NUM]
        fwdr_new_target_params[ACK_ID] = xfer_params_ack_id
        fwdr_new_target_params[REPLY_QUEUE] = self.AT_FOREMAN_ACK_PUBLISH
        target_location = self.archive_name + "@" + self.archive_ip + ":" + target_dir
        fwdr_new_target_params['TARGET_LOCATION'] = target_location

        # This may look curious, but in the other devices, a raft_list is a list of rafts,
        # but a raft_ccd_list is a list of lists, where each ccd sublist refers to 
        # a raft by the same list index
        #
        # This business is really so that unit tests can compare messages to 
        # the canonical versions...as dicts are open ended and can correctly
        # contain more keys than the canonical example and hence fail incorrectly,
        # using lists eliminates this likely possibility.
        xfer_params_dict = {}
        xfer_params_dict['RAFT_LIST'] = []
        xfer_params_dict['RAFT_LIST'].append(self._wfs_raft)
        xfer_params_dict['RAFT_CCD_LIST'] = []
        CCD_LIST = []
        CCD_LIST.append(self._wfs_ccd)
        xfer_params_dict['RAFT_CCD_LIST'].append(CCD_LIST)
        xfer_params_dict['AT_FWDR'] = self._current_fwdr['FQN']
        fwdr_new_target_params['XFER_PARAMS'] = xfer_params_dict
        route_key = self._current_fwdr["CONSUME_QUEUE"]
        #self.prp.pprint(fwdr_new_target_params)
        self.clear_fwdr_state()
        self.publish_message(route_key, fwdr_new_target_params)
       

        
        # receive ack back from forwarder that it has job params
        if self.METRIX:
            z1 = datetime.datetime.now()

        fwdr_response = self.simple_progressive_ack_timer(self.FWDR, 30.0)

        if self.METRIX: 
            z2 = datetime.datetime.now()
            z3 = z2 - z1
            LOGGER.info("METRIX: In StartInt - waited %s for xfer_params ack to return." % z3)

        if fwdr_response == False:
            name = self._current_fwdr['FQN']
            type = "FAULT"
            desc = "No xfer_params response from fwdr."
            LOGGER.critical("No xfer_params response from fwdr.. Setting FAULT state, 5752")
            self.send_fault_state_event("5752", desc, type, name) 
            return


        # accept job by Ack'ing True
        st_int_params_ack = {}
        st_int_params_ack['MSG_TYPE'] = 'AT_START_INTEGRATION_ACK'
        st_int_params_ack['ACK_ID'] = start_int_ack_id
        st_int_params_ack['ACK_BOOL'] = True
        st_int_params_ack['JOB_NUM'] = job_number
        st_int_params_ack['SESSION_ID'] = session_id
        st_int_params_ack['COMPONENT'] = self.COMPONENT_NAME
        self.accept_job(st_int_params_ack)



    def do_fwdr_health_check(self, ack_id):
        """ Send AT_FWDR_HEALTH_CHECK message to at_foreman_ack_publish queue.
            Retrieve available forwarders from ForwarderScoreboard, set their state to
            HEALTH_CHECK, status to UNKNOWN, and publish the message.

            :params ack_id: Ack id for AR forwarder health check.

            :return: Number of health checks sent.
        """
        msg_params = {}
        msg_params[MSG_TYPE] = 'AT_FWDR_HEALTH_CHECK'
        msg_params[ACK_ID] = ack_id
        msg_params[REPLY_QUEUE] = self.AT_FOREMAN_ACK_PUBLISH


        forwarders = list(self._forwarder_dict.keys())
        for x in range (0, len(forwarders)):
            route_key = self._forwarder_dict[forwarders[x]]["CONSUME_QUEUE"]
            msg_params["CONSUME_QUEUE"] = route_key
            if self.DP:
                print("-->do_fwdr_health_check")
                print("x ", x)
                print("route_key ", route_key)
                print("msg_params", msg_params)
                print("<--")
            self.publish_message(route_key, msg_params)
        return len(forwarders)


    def accept_job(self, dmcs_message):
        """ Send AR_START_INTEGRATION_ACK message with ack_bool equals True (job accepted)
            and other job specs to dmcs_ack_consume queue.

            :params dmcs_message: A dictionary that stores info of a job.

            :return: None.
        """
        self.publish_message(self.DMCS_ACK_CONSUME, dmcs_message)


    def refuse_job(self, params, fail_details):
        """ Send AR_START_INTEGRATION_ACK message with ack_bool equals False (job refused)
            and other job specs to dmcs_ack_consume queue.

            Set job state as JOB_REFUSED in JobScoreboard.

            :params parmas: A dictionary that stores info of a job.

            :params fail_details: A string that describes what went wrong, not used for now.

            :return: None.
        """
        dmcs_message = {}
        dmcs_message[JOB_NUM] = params[JOB_NUM]
        dmcs_message[MSG_TYPE] = 'AR_START_INTEGRATION_ACK'
        dmcs_message['ACK_ID'] = params['ACK_ID']
        dmcs_message['SESSION_ID'] = params['SESSION_ID']
        dmcs_message['VISIT_ID'] = params['VISIT_ID']
        dmcs_message['IMAGE_ID'] = params['IMAGE_ID']
        dmcs_message[ACK_BOOL] = False 
        dmcs_message['COMPONENT'] = self.COMPONENT_NAME
        self.JOB_SCBD.set_value_for_job(params[JOB_NUM], STATE, "JOB_REFUSED")
        self.publish_message(self.DMCS_ACK_CONSUME, dmcs_message)


    def process_at_end_readout(self, params):
        """ Set job state as PREPARE_READOUT in JobScoreboard.
            Send readout to forwarders.
            Set job state as READOUT_STARTED in JobScoreboard.
            Wait to retrieve and process readout responses.

            :params parmas: A dictionary that stores info of a job.

            :return: None.
        """
        LOGGER.info('process_at_end_readout: RECEIVING END_READOUT MESSAGE')
        LOGGER.debug('Incoming message to process_at_end_readout is: %s', pformat(str(params)))

        if self.do_health_check() == False:
            LOGGER.critical("No health check response from ANY fwdr. Setting FAULT state, 5751")
            desc = "No health check response from ANY fwdr"
            self.send_fault_state_event("5751", desc, 'FAULT', 'FORWARDER' ) # error code for 'no health check response any fwdrs'
            return

        reply_queue = params['REPLY_QUEUE']
        readout_ack_id = params[ACK_ID]
        job_number = params[JOB_NUM]
        image_id = params['IMAGE_ID']
        msgtype = params[MSG_TYPE]


        ### FIX - Note: Incorporate way for simple_prog timer to do health checks.
        #self.ack_timer(2.0)


        # send readout to forwarder
        fwdr_readout_ack = self.get_next_timed_ack_id("AT_FWDR_END_READOUT_ACK")
        msg = {}
        msg[MSG_TYPE] = 'AT_FWDR_END_READOUT'
        msg[JOB_NUM] = job_number
        msg[SESSION_ID] = params[SESSION_ID]
        msg['IMAGE_ID'] = image_id
        msg[ACK_ID] = fwdr_readout_ack
        msg['REPLY_QUEUE'] = self.AT_FOREMAN_ACK_PUBLISH
        msg['IMAGE_SEQUENCE_NAME'] = params['IMAGE_SEQUENCE_NAME']
        msg['IMAGES_IN_SEQUENCE'] = params['IMAGES_IN_SEQUENCE']
        msg['IMAGE_INDEX'] = params['IMAGE_INDEX']
        if self.DP:
            print("self._current_fwdr = ",self._current_fwdr)
        route_key = self._current_fwdr['CONSUME_QUEUE']
        self.publish_message(route_key, msg)

        # Now, ack processor will deal with result sets if they arrive...if end readout ack
        # does not arrive, then lack of ack is noted against that job_num, IF checksumming
        # is set to true.
        return

        """
        readout_response = self.simple_progressive_ack_timer(self.FWDR, 30.0)

        if readout_response == False:
            name = self._current_fwdr['FQN']
            desc = "No AT_FWDR_END_READOUT response from " + str(name)
            type = "FAULT"
            LOGGER.critical("No AT_FWDR_END_READOUT response from %s for job %s. Setting FAULT state, 5752" % 
                           (name,job_number))
            self.send_fault_state_event(5752, desc, type, name)

            return

        result_set = self.did_current_fwdr_send_result_set()
        if result_set == None:  #fail, ack_bool is false, and filename_list is None
            final_msg = {}
            final_msg['MSG_TYPE'] = msgtype + "_ACK"
            final_msg['ACK_ID'] = readout_ack_id
            final_msg['ACK_BOOL'] = False
            final_msg['JOB_NUM'] = job_number
            final_msg[IMAGE_ID] = image_id
            final_msg['COMPONENT'] = self.COMPONENT
            final_msg['RESULT_SET'] = {}
            flist = []
            rlist = []
            final_msg['RESULT_SET']['FILENAME_LIST'] = flist
            final_msg['RESULT_SET']['RECEIPT_LIST'] = rlist
            self.publish_message(reply_queue, final_msg)
        else:
            if self.use_archive_ctrl == False:
                final_msg = {}
                final_msg['MSG_TYPE'] = msgtype + "_ACK"
                final_msg['ACK_ID'] = readout_ack_id
                final_msg['ACK_BOOL'] = True
                final_msg['JOB_NUM'] = job_number
                final_msg['COMPONENT'] = self.COMPONENT
                final_msg[IMAGE_ID] = image_id
                rlist = []
                final_msg['RESULT_SET'] = {}
                final_msg['RESULT_SET']['FILENAME_LIST'] = result_set['FILENAME_LIST']
                final_msg['RESULT_SET']['RECEIPT_LIST'] = rlist  #no arch_ctrl, no receipts
                self.publish_message(reply_queue, final_msg)
                return
            else:
                pass
                self.process_readout_responses(readout_ack_id, msgtype, reply_queue, image_id, job_number, result_set)
        """

    def process_readout_responses(self, readout_ack_id, msgtype, reply_queue, image_id, job_number, result_set):
        self.clear_archive_ack()
        archive_readout_ack = self.get_next_timed_ack_id("AT_ITEMS_XFERD_ACK")
        xferd_list_msg = {}
        xferd_list_msg[MSG_TYPE] = 'AT_ITEMS_XFERD'
        xferd_list_msg[ACK_ID] = archive_readout_ack
        xferd_list_msg['REPLY_QUEUE'] = self.AT_FOREMAN_ACK_PUBLISH
        xferd_list_msg['RESULT_SET'] = result_set
        self.publish_message(self.ARCHIVE_CTRL_CONSUME, xferd_list_msg) 
           
        xferd_responses = self.simple_progressive_ack_timer(self.ARCHIVE, 8.0) 

        if xferd_responses == False:
            final_msg = {}
            final_msg['MSG_TYPE'] = msgtype + "_ACK"
            final_msg['COMPONENT'] = self.COMPONENT
            final_msg['ACK_ID'] = readout_ack_id
            final_msg['ACK_BOOL'] = False
            final_msg['JOB_NUM'] = job_number
            final_msg[IMAGE_ID] = image_id
            final_msg['RESULT_SET'] = {}
            flist = []
            rlist = []
            final_msg['RESULT_SET']['FILENAME_LIST'] = flist
            final_msg['RESULT_SET']['RECEIPT_LIST'] = rlist
            self.publish_message(reply_queue, final_msg)

            return

        results = self._archive_ack['RESULT_SET']

        ack_msg = {}
        ack_msg['MSG_TYPE'] = 'AT_READOUT_ACK'
        ack_msg['JOB_NUM'] = job_number
        ack_msg['COMPONENT'] = self.COMPONENT_NAME
        ack_msg['ACK_ID'] = readout_ack_id
        ack_msg['ACK_BOOL'] = True
        ack_msg['RESULT_LIST'] = results
        self.publish_message(reply_queue, ack_msg)


    def process_header_ready_event(self, params):
        if self.do_health_check() == False:
            LOGGER.critical("No health check response from ANY fwdr. Setting FAULT state, 5751")
            desc = "No health check response from ANY fwdr"
            self.send_fault_state_event("5751", desc, 'FAULT', 'FORWARDER' ) # error code for 'no health check response any fwdrs'
            return
        hr_ack_id = self.get_next_timed_ack_id('AT_FWDR_HEADER_READY_ACK')

        fname = params['FILENAME']
        image_id = params['IMAGE_ID']
        msg = {}
        msg['MSG_TYPE'] = 'AT_FWDR_HEADER_READY'
        msg['FILENAME'] = fname
        msg['IMAGE_ID'] = image_id
        msg['ACK_ID'] = hr_ack_id
        msg[REPLY_QUEUE] = self.AT_FOREMAN_ACK_PUBLISH

        route_key = self._current_fwdr['CONSUME_QUEUE']

        self.publish_message(route_key, msg)

        # Uncomment if it is desired to confirm header ready msg reached fwdr
        #hr_response = self.simple_progressive_ack_timer(self.FWDR, 6.0)

    def clear_fwdr_state(self):
        fwdrs = list(self._fwdr_state_dict.keys())
        for fwdr in fwdrs:
            self._fwdr_state_dict[fwdr] = {}
            self._fwdr_state_dict[fwdr]['RESPONSE'] = UNKNOWN

    def clear_archive_ack(self):
        self._archive_ack = {}
        self._archive_ack['RESPONSE'] = UNKNOWN


    def setup_fwdr_state_dict(self):
        """ The _fwdr_state_dict is a simple hash used to store ACK
            responses from Forwarders. The very busy commandable devices
            such as the ArchiveDevice and the PromptProcessDevice use
            a Redis scoreboard structure to keep track of who is responsive 
            and who is not. Because the ATArchiver will have just one Forwarder
            and one spare, A redis instance is not justified, hence keeping
            the code simpler.
            For each ATArchiver operation where an ACK is expected, this dict is used.
        """
        LOGGER.info("Setting up Forwarder state dict for AT")
        self._fwdr_state_dict = {}
        fwdrs = list(self._forwarder_dict.keys())
        for fwdr in fwdrs:
            res = {'RESPONSE':'UNKNOWN'}
            self._fwdr_state_dict[fwdr] = deepcopy(res)

        LOGGER.info("Forwarder dict is: %s" % pformat(self._forwarder_dict))
        LOGGER.info("Forwarder state dict is: %s" % pformat(self._fwdr_state_dict))

 
    def set_fwdr_state(self, component, state):
        if self.DP:
            print("\n\nIn set_fwdr_state - Setting %s state to %s\n" % (component, state))
        LOGGER.info("set_fwdr_state - setting component %s to %s\n" % (component, state))
        self._fwdr_state_dict[component]['RESPONSE'] = state


    def is_current_fwdr_set(self):
        if self._current_fwdr is None:
            return False
        return True

    # FIXME: This, and as noted below, always grabs the
    # first forwarder encountered and uses that forwarder to send messages
    # to.  This is used repeatedly throughout the code, which is the wrong thing
    # to do if we're going to have to send directed messages to multiple forwarders.
    def set_current_fwdr(self):
        self._current_fwdr = None
        fwdrs = list(self._fwdr_state_dict.keys())
        for fwdr in fwdrs:   # Choose the first healthy forwarder encountered
            if self._fwdr_state_dict[fwdr]['RESPONSE'] == HEALTHY:
                tmp_forwarder_dict = deepcopy(self._forwarder_dict[fwdr])
                tmp_forwarder_dict['FQN'] = fwdr
                #self._current_fwdr[fwdr] = tmp_forwarder_dict
                self._current_fwdr = tmp_forwarder_dict
                LOGGER.info("self._current_fwdr " % self._current_fwdr)
                return True
        return False  #Could not find a HEALTHY forwarder to use...:(


    def did_current_fwdr_respond(self):
        if self._fwdr_state_dict[self._current_fwdr['FQN']]['RESPONSE'] == 'RESPONSIVE':
            return True

        return False


    def did_archive_respond(self):
        if self._archive_ack['RESPONSE'] == 'RESPONSIVE':
            return True

        return False


    def did_current_fwdr_send_result_set(self):
        if self._use_mutex:
            self.my_mutex_lock.acquire()
        try:
            if self._fwdr_state_dict[self._current_fwdr['FQN']]['ACK_BOOL'] == True:
                return self._fwdr_state_dict[self._current_fwdr['FQN']]['RESULT_SET']
        except KeyError as e:
            LOGGER.error("The message stored in self._fwdr_state_dict does not have an ACK_BOOL field.")
            LOGGER.error("KeyError exception is %s" % e)
            return None
        finally:
            if self._use_mutex:
                self.my_mutex_lock.release()

        return None


    def confirm_fwdr_state_dict_entry(self, component):
        if(self._fwdr_state_dict[component]['RESPONSE'] == HEALTHY):
            return True

        return False


    def process_ack(self, params):
        """ Add new ACKS for a particular ACK_ID to the Ack Scoreboards
            where they are collated.

            :params: New ack to be checked in.

            :return: None.
        """
        pass
        #self.ACK_SCBD.add_timed_ack(params)
        

    def process_health_check_ack(self, params):
        """ Add new Health Check ACKS to self._fwdr_state_dict
            where they are collated.

            :params: New ack to be checked in.

            :return: None.
        """
        LOGGER.info('In top of process_health_check_ack')
        LOGGER.info('Message from process_health_chech_ack is: %s', pformat(str(params)))
        component = params[COMPONENT]  # The component is the name of the fwdr responding
        self.set_fwdr_state(component, HEALTHY)
       
 
    def process_new_at_item_ack(self, params):
        self._archive_ack['RESPONSE'] = 'RESPONSIVE'
        self._archive_ack['TARGET_DIR'] = params['TARGET_DIR']
        

    def process_xfer_params_ack(self, params):
        if self.DP:
            print("\n\nIn process_xfer_params_ack - auxdevice setting state of %s to RESPONSIVE\n" \
                   % params['COMPONENT'])
        LOGGER.info('process_xfer_params_ack: state of %s being set to RESPONSIVE' %  params['COMPONENT'])
        component = params[COMPONENT]  # The component is the name of the fwdr responding
        self.set_fwdr_state(component, RESPONSIVE)
   
 
    
    def process_at_fwdr_end_readout_ack(self, params):
        component = params[COMPONENT]  # The component is the name of the fwdr responding
        if self._use_mutex:
            LOGGER.debug('Acquireing mutex in process fwdr end readout...')
            self.my_mutex_lock.acquire()
        try:
            self.set_fwdr_state(component, RESPONSIVE)
            ack_bool = params[ACK_BOOL]  # The component is the name of the fwdr responding
            if ack_bool == True:
                self._fwdr_state_dict[component]['ACK_BOOL'] = True
                self._fwdr_state_dict[component]['RESULT_SET'] = params['RESULT_SET']
            else:
                self._fwdr_state_dict[component]['ACK_BOOL'] = False
                self._fwdr_state_dict[component]['RESULT_SET'] = None
        finally:
            LOGGER.debug('At end of critical section of process at fwdr end readout ack')
            # Then just pass for now...

            if self._use_mutex:
                LOGGER.debug('Releasing mutex...')
                self.my_mutex_lock.release()
    

    
    def process_at_items_xferd_ack(self, params):
        self._archive_ack['RESPONSE'] = 'RESPONSIVE'
        self._archive_ack['RESULT_SET'] = params['RESULT_SET']

   
 
    def process_header_ready_ack(self, params):
        component = params[COMPONENT]  # The component is the name of the fwdr responding
        self.set_fwdr_state(component, RESPONSIVE)



    def get_next_timed_ack_id(self, ack_type):
        """ Increment ack id by 1, and store it.
            Return ack id with ack type as a string.

            :params ack_type: Informational string to prepend Ack ID.

            :return retval: String with ack type followed by next ack id.
        """
        n = datetime.datetime.now()
        datestring = n.strftime("%Y-%m-%d_%H_%M_%S")+"-"
        self._next_timed_ack_id = self._next_timed_ack_id + 1
        val = (ack_type + "_" + datestring + str(self._next_timed_ack_id).zfill(6))
        return val



    def set_session(self, params):
        pass
        """ Record new session in JobScoreboard.
            Send AR_NEW_SESSION_ACK message with ack_bool equals True to specified reply queue.

            :params params: Dictionary with info about new session.

            :return: None.
        self.JOB_SCBD.set_session(params['SESSION_ID'])
        ack_id = params['ACK_ID']
        msg = {}
        msg['MSG_TYPE'] = 'AR_NEW_SESSION_ACK'
        msg['COMPONENT'] = self.COMPONENT_NAME
        msg['ACK_ID'] = ack_id
        msg['ACK_BOOL'] = True
        route_key = params['REPLY_QUEUE'] 
        self.publish_message(route_key, msg)
        """



    def set_visit(self, params):
        """ Set current visit_id in JobScoreboard.
            Send AR_NEXT_VISIT_ACK message with ack_bool equals True to specified reply queue.

            :params params: Message dictionary with info about new visit.

            :return: None.
        """
        bore_sight = params['BORE_SIGHT']
        self.JOB_SCBD.set_visit_id(params['VISIT_ID'], bore_sight)
        ack_id = params['ACK_ID']
        msg = {}
        ## XXX FIXME Do something with the bore sight in params['BORE_SIGHT']
        msg['MSG_TYPE'] = 'AR_NEXT_VISIT_ACK'
        msg['COMPONENT'] = self.COMPONENT_NAME
        msg['ACK_ID'] = ack_id
        msg['ACK_BOOL'] = True
        route_key = params['REPLY_QUEUE'] 
        self.publish_message(route_key, msg)



    def get_current_visit(self):
        """ Retrieve current visit from JobSocreboard.

            :params: None.

            :return: Current visit returned by JobSocreboard.
        """
        return self.JOB_SCBD.get_current_visit()
        

    def ack_timer(self, seconds):
        """ Sleeps for user-defined seconds.

            :params seconds: Time to sleep in seconds.

            :return: True.
        """
        sleep(seconds)
        return True


    def progressive_ack_timer(self, ack_id, expected_replies, seconds):
        """ Sleeps for user-defined seconds, or less if everyone has reported back in.

            :params ack_id: Ack ID to wait for.

            :params expected_replies: Number of components expected to ack..

            :params seconds: Maximum time to wait in seconds.

            :return: The dictionary that represents the responses from the components ack'ing.
                     Note: If only one component will ack, this method breaks out of its
                           loop after the one ack shows up - effectively beating the maximum
                           wait time.
        """
        counter = 0.0
        while (counter < seconds):
            counter = counter + 0.5
            sleep(0.5)
            response = self.ACK_SCBD.get_components_for_timed_ack(ack_id)
            if response == None:
                continue
            if len(list(response.keys())) == expected_replies:
                return response

        ## Try one final time
        response = self.ACK_SCBD.get_components_for_timed_ack(ack_id)
        if response == None:
            return None
        elif len(list(response.keys())) == expected_replies:
            return response
        else:
            return None


    def simple_progressive_ack_timer(self, type, seconds):
        counter = 0.0
        while (counter < seconds):
            counter = counter + 0.5
            sleep(0.3)
            if type == self.FWDR:
                if self.did_current_fwdr_respond(): 
                    return True
            elif type == self.ARCHIVE:
                if self.did_archive_respond(): 
                    return True

        ## Try one final time
        if type == self.FWDR:
            if self.did_current_fwdr_respond():
                return True
        elif type == self.ARCHIVE:
            if self.did_archive_respond(): 
                sleep(0.3) # Some time for ack thread to finish writing...
                return True
        else:
            return False


    def send_fault_state_event(self, error_code, desc, type, comp):
        msg_params = {}
        msg_params[MSG_TYPE] = "FAULT"
        msg_params['COMPONENT'] = comp
        msg_params['DEVICE'] = self.DEVICE
        msg_params['FAULT_TYPE'] = type
        msg_params['ERROR_CODE'] = error_code
        msg_params['DESCRIPTION'] = desc
        self.publish_message(self.DMCS_FAULT_CONSUME, msg_params)


    def extract_config_values(self, filename):
        """ Parse system config yaml file.
            Throw error messages if Yaml file or key not found.

            :params: None.

            :return: True.
        """
        cdm = None
        try:
            cdm = self.loadConfigFile(filename)
        except IOError as e:
            LOGGER.critical("Unable to find CFG Yaml file %s\n" % self._config_file)
            sys.exit(101)

        try:
            self._base_broker_addr = cdm[ROOT][BASE_BROKER_ADDR]
            self._forwarder_dict = cdm[ROOT][XFER_COMPONENTS]['AUX_FORWARDERS']
            self._wfs_raft = cdm[ROOT]['ATS']['WFS_RAFT']
            self._wfs_ccd = cdm[ROOT]['ATS']['WFS_CCD']
            self._use_mutex = False
            if cdm[ROOT]['USE_MUTEX'] == "YES":
                self._use_mutex = True

            # Placeholder until eventually worked out by Data Backbone team
            self.use_archive_ctrl = cdm[ROOT]['ARCHIVE']['USE_ARCHIVE_CTRL']
            self.archive_fqn = cdm[ROOT]['ARCHIVE']['ARCHIVE_NAME']
            self.archive_name = cdm[ROOT]['ARCHIVE']['ARCHIVE_LOGIN']
            self.archive_ip = cdm[ROOT]['ARCHIVE']['ARCHIVE_IP']
            self.archive_xfer_root = cdm[ROOT]['ARCHIVE']['ARCHIVE_XFER_ROOT']
        except KeyError as e:
            print("Dictionary error: %s" % e)
            print("Bailing out...")
            LOGGER.critical("CFG dictionary key error: %s" % e)
            LOGGER.critical("Bailing out...")
            sys.exit(99)

        self._base_msg_format = 'YAML'

        if 'BASE_MSG_FORMAT' in cdm[ROOT]:
            self._base_msg_format = cdm[ROOT]['BASE_MSG_FORMAT']
        return cdm


    def wait_for_forwarder(self):
        self.clear_fwdr_state()
        health_check_ack_id = self.get_next_timed_ack_id('AT_FWDR_HEALTH_CHECK_ACK')
        num_fwdrs_checked = self.do_fwdr_health_check(health_check_ack_id)
        while self.set_current_fwdr() is False:
            LOGGER.info("wait for forwarder: No forwarder set. trying to set one up")
            # Give fwdrs enough time to respond and set self._current_fwdr
            # TODO - THIS sleep IS A TERRIBLE WAY TO DO THIS...
            # when we upgrade to Pika 1.0, investigate changing this to watch for consume-ok
            # we can't do that now because it's not part of this version's current API
            time.sleep(1)

    def setup_forwarder_thread(self):
        kws = {}
        md = {}
        md['amqp_url'] = self.base_broker_url
        md['name'] = 'Thread-at_foreman_ack_publish'
        md['queue'] = 'at_foreman_ack_publish'
        md['callback'] = self.on_ack_message
        md['format'] = "YAML"
        md['test_val'] = 'test_it'
        md['publisher_name'] = 'on_ack_message_publisher'
        md['publisher_url'] = self.pub_base_broker_url
        #kws[md['name']] = md
        kws['at_foreman_ack_publish'] = md
        self.add_thread_groups(kws)

    def setup_consumer_threads(self):
        """ Create ThreadManager object with base broker url and kwargs to setup consumers.

            :params: None.

            :return: None.
        """


        # Set up kwargs that describe consumers to be started
        kws = {}
        md = {}
        md['amqp_url'] = self.base_broker_url
        md['name'] = 'Thread-aux_foreman_consume'
        md['queue'] = 'at_foreman_consume'
        md['callback'] = self.on_aux_foreman_message
        md['format'] = "YAML"
        md['test_val'] = None
        md['publisher_name'] = 'on_aux_foreman_message_publisher'
        md['publisher_url'] = self.pub_base_broker_url
        #kws[md['name']] = md
        kws['aux_foreman_consume'] = md

        md = {}
        md['amqp_url'] = self.base_broker_url
        md['name'] = 'Thread-archive_ctrl_publish'
        md['queue'] = 'archive_ctrl_publish'
        md['callback'] = self.on_archive_message
        md['format'] = "YAML"
        md['test_val'] = 'test_it'
        md['publisher_name'] = 'on_archive_message_publisher'
        md['publisher_url'] = self.pub_base_broker_url
        #kws[md['name']] = md
        kws['archive_ctrl_publish'] = md

        self.add_thread_groups(kws)


    def send_telemetry(self, status_code, description):
        msg = {}
        msg['MSG_TYPE'] = 'TELEMETRY'
        msg['DEVICE'] = self.DEVICE
        msg['STATUS_CODE'] = status_code
        msg['DESCRIPTION'] = description
        self.publish_message(self.TELEMETRY_QUEUE, msg)



if __name__ == "__main__":
    atArchiver = ATArchiver('L1SystemCfg.yaml')


    atArchiver.register_SIGINT_handler()

    LOGGER.info('ATArchiver Init complete')
    print("ATArchiver initialization completed. Running.")

    signal.pause()
    LOGGER.info('ATArchiver shutdown complete.  Exiting.')
    print('ATArchiver shutdown complete.  Exiting.')
    os._exit(0)
