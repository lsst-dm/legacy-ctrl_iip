import pika
from Scratchpad import Scratchpad
from toolsmod import get_timestamp
from toolsmod import get_epoch_timestamp
import yaml
import sys
import time
import hashlib
import os.path
import logging
import os
import copy
import subprocess
import _thread
#import pyfits 
#import numpy as np
from const import *
from Consumer import Consumer
from SimplePublisher import SimplePublisher


class Forwarder:
    """ Set and read info about job from Scratchpad.py.
    
        Use those info to respond to health check and other requests from other devices
        through sending message back to the reply queue. 
    
        Forward ccd files from .data files to .fits files.
        
        Presents a vanilla L1 Forwarder personality. In nightly operation, at least 21 
        of these components will be available at any time (one for each raft).
        A resource group will be used to satisfy L1 tasks such as prompt processing for 
        alerts, archiving, and spectrograph.
    """

    def __init__(self):
        """ Try to extract config values from yaml file, raise KeyError otherwise.
            Set home directory, _base_broker_url.
            Store handler methods for each message type. 
            Set up publishers, scoreboards, and consumer threads.
            Initiate Scratchpad with _base_broker_url.

            :params: None.

            :return: None.
        """        
        self._registered = False
        f = open('ForwarderCfg.yaml')
        #cfg data map...
        cdm = yaml.safe_load(f)
        try:
            self._name = cdm[NAME]
            self._passwd = cdm[PASSWD]
            self._fqn = cdm[FQN]
            self._base_broker_addr = cdm[BASE_BROKER_ADDR]
            self._consume_queue = cdm[CONSUME_QUEUE]
            #self._publish_queue = cdm[PUBLISH_QUEUE]
            self._hostname = cdm[HOSTNAME]
            self._ip_addr = cdm[IP_ADDR]
            self._DAQ_PATH = cdm['DAQ_PATH']
            ## XXX FIX: Put in config file
            self.CHECKSUM_ENABLED = False 
        except KeyError as e:
            print("Missing base keywords in yaml file... Bailing out...")
            sys.exit(99)

        #self._DAQ_PATH = "/home/F1/xfer_dir/"
        self._home_dir = "/home/" + self._name + "/"
        self._base_broker_url = "amqp://" + self._name + ":" + self._passwd + "@" + str(self._base_broker_addr)

        self._msg_actions = { FORWARDER_HEALTH_CHECK: self.process_health_check,
                              FORWARDER_JOB_PARAMS: self.process_job_params,
                              'AR_FWDR_XFER_PARAMS': self.process_job_params,  # Here if AR case needs different handler
                              'AR_FWDR_READOUT': self.process_foreman_readout,
                              FORWARDER_READOUT: self.process_foreman_readout }

        self.setup_publishers()
        self.setup_consumers()
        self._job_scratchpad = Scratchpad(self._base_broker_url)


    def setup_publishers(self):
        """ Initiate SimplePublisher with _base_broker_url. 
        
            :params: None.

            :return: None.
        """
        self._publisher = SimplePublisher(self._base_broker_url)

 
    def setup_consumers(self):
        """ Initiate treadname and try to start a new consumer thread with treadname and
            2s of delay. Exit if have error.

            :params: None.

            :return: None.
        """
        threadname = "thread-" + self._consume_queue
        print("Threadname is %s" % threadname)

        self._consumer = Consumer(self._base_broker_url, self._consume_queue)
        try:
            _thread.start_new_thread( self.run_consumer, (threadname, 2,) )
            print("Started Consumer Thread")
        except:
            sys.exit(99)


    def run_consumer(self, threadname, delay):
        self._consumer.run(self.on_message)


    def on_message(self, ch, method, properties, body):
        """ Calls the appropriate Forwarder message action handler according to 
            message type.
        
            :params ch: Channel to message broker.
            :params method: Delivery method from Pika, unused unless testing.
            :params properties: Properties of DMCS callback message body, unused unless 
                                testing.
            :params body: A dictionary that stores the message body.
            
            :return: None.
        """
        ch.basic_ack(method.delivery_tag) 
        print("INcoming PARAMS, body is:\n%s" % body)
        msg_dict = body

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)


    def process_health_check(self, params):
        """ Send health status of forwarders back through FORWARDER_HEALTH_CHECK_ACK 
            message.

            :params params: A dictionary that stores info about forwarders.

            :return: None.
        """
        self.send_ack_response("FORWARDER_HEALTH_CHECK_ACK", params)


    def process_job_params(self, params):
        """ Get job and xfer params and remove fits files in xfer_dir.
            Store ccd list, login string, target directory (where to put file) and 
            filename in Scratchpad.
            Store job state as READY_WITH_PARAMS in Scratchpad.
            Send back FORWARDER_JOB_PARAMS_ACK message to show that job params are set.

            :params params: A dictionary that stores info about job.

            :return: None.
        """
        job_params = copy.deepcopy(params)
        xfer_params = job_params['TRANSFER_PARAMS']

        # Also RM fits files in xfer_dir
        cmd = "rm " + self._DAQ_PATH + "*.fits"
        os.system(cmd)


        filename_stub = str(job_params['JOB_NUM']) + "_" + str(job_params['VISIT_ID']) + "_" + str(job_params['IMAGE_ID']) + "_"

        login_str = str(xfer_params['DISTRIBUTOR']['NAME']) + "@" + str(xfer_params['DISTRIBUTOR']['IP_ADDR']) + ":"

        target_dir = str(xfer_params['DISTRIBUTOR']['TARGET_DIR'])

        #xfer_params = transfer_params['XFER_PARAMS']
        s_params = {}
        s_params['CCD_LIST'] = xfer_params['CCD_LIST']
        s_params['LOGIN_STR'] = login_str
        s_params['TARGET_DIR'] = target_dir
        s_params['FILENAME_STUB'] = filename_stub

        print("S_params are: %s" % s_params)
        
        # Now, s_params should have all we need for job. Place as value for job_num key 
        self._job_scratchpad.set_job_transfer_params(params[JOB_NUM], s_params)
        self._job_scratchpad.set_job_state(params['JOB_NUM'], "READY_WITH_PARAMS")

        self.send_ack_response('FORWARDER_JOB_PARAMS_ACK', params)


    def process_foreman_readout(self, params):
        """ Get a dictionary of raw ccd files and format them into fits files for each 
            ccd.
            
            Call forward to move data from camera to archive or NCSA for science 
            processing.
            
            Send AR_ITEMS_XFERD_ACK message back to indicate that work is done.
            
            :params params: A dictionary that stores info about job.

            :return: None.
        """
        # self.send_ack_response("FORWARDER_READOUT_ACK", params)
        reply_queue = params['REPLY_QUEUE']

        job_number = params[JOB_NUM]
        # Check and see if scratchpad has this job_num
        if job_number not in list(self._job_scratchpad.keys()):
            # Raise holy hell...
            pass

        # raw_files_dict is of the form { ccd: filename} like { 2: /home/F1/xfer_dir/ccd_2.data
        raw_files_dict = self.fetch(job_number)

        final_filenames = self.format(job_number, raw_files_dict)

        results = self.forward(job_number, final_filenames)

        msg = {}
        msg['MSG_TYPE'] = 'AR_ITEMS_XFERD_ACK'
        msg['JOB_NUM'] = job_number
        msg['IMAGE_ID'] = params['IMAGE_ID']
        msg['COMPONENT'] = self._fqn
        msg['ACK_ID'] = params['ACK_ID']
        msg['ACK_BOOL'] = True  # See if num keys of results == len(ccd_list) from orig msg params
        msg['RESULT_LIST'] = results
        self._publisher.publish_message(reply_queue, msg)



    def fetch(self, job_num):
        """ Retrieve the ccds in a job. Create raw_files_dict to store ccds and their 
            filenames.

            :params job_num: Job number.

            :return: None.
        """
        raw_files_dict = {}
        ccd_list = self._job_scratchpad.get_job_value(job_num, 'CCD_LIST')
        for ccd in ccd_list:
            filename = "ccd_" + str(ccd) + ".data"
            raw_files_dict[ccd] = filename

        print("In Forwarder Fetch method, raw_files_dict is: \n%s" % raw_files_dict)
        return raw_files_dict


    """
        format raw files to fits file with header data
        :param file_list: dictionary of file_name against raw file name 
        :param mdata: primary meta data stream fetched from camera daq
    """ 
    ## FIX: The two format methods have the same numbers of parameters. Probably comment one out
    def format(self, file_list, mdata): 
        final_filenames = [] 
        for ccd_id, raw_file_name in file_list.items(): 
            image_array = np.fromfile(raw_file_name, dtype=np.int32)
            header_data = mdata[ccd_id]["primary_metadata_chunk"]
            secondary_data = mdata[ccd_id]["secondary_metadata_chunk"]
            header_data.update(secondary_data)

            primary_header = pyfits.Header()
            for key, value in header_data.items(): 
                primary_header[key] = value
            fits_file = pyfits.PrimaryHDU(header=primary_header, data=image_array)
            fits_file.writeto(ccd_id + ".fits")
            final_filenames.append(ccd_id + ".fits")
        return final_filenames

    def format(self, job_num, raw_files_dict):
        """ For each ccd, add its header, data path, and timestamp to its fits file.
            Return the dictionary of fits file for each ccd.
            
            :params job_num: Job number.
            :params raw_files_dict: Dictionary of ccds and their .data file paths.

            :return final_filenames: Dictionary of ccds and their .fits file paths.
        """
        keez = list(raw_files_dict.keys())
        filename_stub = self._job_scratchpad.get_job_value(job_num, 'FILENAME_STUB')
        final_filenames = {}
        for kee in keez:
            final_filename = filename_stub + "_" + kee + ".fits"
            target = self._DAQ_PATH + final_filename
            print("Final filename is %s" % final_filename) 
            print("target is %s" % target) 
            cmd1 = 'cat ' + self._DAQ_PATH + "ccd.header" + " >> " + target
            cmd2 = 'cat ' + self._DAQ_PATH + raw_files_dict[kee] + " >> " + target
            dte = get_epoch_timestamp()
            print("DTE IS %s" % dte)
            cmd3 = 'echo ' + str(dte) +  " >> " + target
            print("cmd1 is %s" % cmd1)
            print("cmd2 is %s" % cmd2)
            os.system(cmd1)
            os.system(cmd2)
            os.system(cmd3)
            final_filenames[kee] = final_filename 
            
            print("Done in format()...file list is: %s" % final_filenames)

        print("In format method, final_filenames are:\n%s" % final_filenames)
        return final_filenames        


    def forward(self, job_num, final_filenames):
        """ Read .fits file for each ccd and store ccds, md5 encrypted data, and filenames
            for all ccds into a list in results dict.
            Send .fits file to server (login_str) in target_dir directory under the same
            filename.
            
            :params job_num: Job number.
            :params final_filenames: Dictionary of ccds and their .fits file paths.

            :return results: Dictionary that stores lists of ccds, their .fits file paths,
                             and md5 encrypted data.
        """
        ## FIX: change CHECKSUM_ENABLED in init
        print("Start Time of READOUT IS: %s" % get_timestamp())
        login_str = self._job_scratchpad.get_job_value(job_num, 'LOGIN_STR')
        target_dir = self._job_scratchpad.get_job_value(job_num, 'TARGET_DIR')
        results = {}
        CCD_LIST = []
        FILENAME_LIST = []
        CHECKSUM_LIST = []
        ccds = list(final_filenames.keys())
        for ccd in ccds:
            final_file = final_filenames[ccd]
            pathway = self._DAQ_PATH + final_file
            with open(pathway) as file_to_calc:
                if self.CHECKSUM_ENABLED:
                    data = file_to_calc.read()
                    resulting_md5 = hashlib.md5(data).hexdigest()
                else:
                    resulting_md5 = '0'
                minidict = {}
                CCD_LIST.append(ccd)
                CHECKSUM_LIST.append(resulting_md5)
                FILENAME_LIST.append(target_dir + final_file)
                cmd = 'scp ' + pathway + " " + login_str + target_dir + final_file
                print("Finish Time of SCP'ing %s IS: %s" % (pathway, get_timestamp()))
                print("In forward() method, cmd is %s" % cmd)
                os.system(cmd)
                results['CCD_LIST'] = CCD_LIST
                results['FILENAME_LIST'] = FILENAME_LIST
                results['CHECKSUM_LIST'] = CHECKSUM_LIST

        print("END Time of READOUT XFER IS: %s" % get_timestamp())
        print("In forward method, results are: \n%s" % results)
        return results
            
        #cmd = 'cd ~/xfer_dir && scp -r $(ls -t)' + ' ' + str(self._xfer_login) + ':xfer_dir'
        #pass


    def send_ack_response(self, type, params):
        """ Send forwarder responses for ack_id back through message. 

            :params type: Message type.
            :params params: A dictionary that stores info about the response.

            :return: None.
        """
        timed_ack = params.get("ACK_ID")
        job_num = params.get(JOB_NUM)
        response_queue = params['RESPONSE_QUEUE']
        msg_params = {}
        msg_params[MSG_TYPE] = type
        msg_params[JOB_NUM] = job_num
        msg_params['COMPONENT'] = self._fqn
        msg_params[ACK_BOOL] = "TRUE"
        msg_params[ACK_ID] = timed_ack
        self._publisher.publish_message(response_queue, msg_params)


    def register(self):
        """ None.
        
            :params: None.

            :return: None.
        """
        pass
        # pass in msg to foreman stating cfg settings
        # pass in name of special one time use queue that will be deleted afterwards
        # Returm message will have a possible delta...
        # If return NAME is different, consume queue will need to be changed
        # and self._home_dir will need repairing, possibly more.



def main():
    fwd = Forwarder()
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print("")
    print("Forwarder Finished")


"""
Saved here for temp...
###########XXXXXXXXXXXXXXX##############
#### 3 F's go here...Fetch, Format and Forward

        # Fetch
        # Check presence of file
        ## If not there, ack false
        ## If there, pull file and break into arrays

        # Still one conection for both files, but files are sent to scp in proper xfer order
        #FIX ':xfer_dir' must be changed to a mutable target dir...
        cmd = 'cd ~/xfer_dir && scp -r $(ls -t)' + ' ' + str(self._xfer_login) + ':xfer_dir'

#### After file forwarded, send finished ACK...
        #remove datetime line below for production
        datetime2 = get_timestamp()
        proc = subprocess.check_output(cmd, shell=True)
        LOGGER.info('%s readout message action; command run in os at %s is: %s ',self._name, datetime1, cmd)
        LOGGER.info('File xfer command completed (returned) at %s', datetime2)
        msg_params = {}
        msg_params[MSG_TYPE] = 'XFER_COMPLETE'
        msg_params['COMPONENT'] = 'FORWARDER'
        msg_params['JOB_NUM'] = params[JOB_NUM]
        msg_params[NAME] = self._name
        msg_params['EVENT_TIME'] = "Transfer completion time = %s" % datetime2
        msg_params['SOURCE_DIR'] = source_dir
        msg_params['COMMAND'] = cmd
        self._publisher.publish_message('reports', yaml.dump(msg_params))
###########XXXXXXXXXXXXX###############
"""

if __name__ == "__main__": main()

