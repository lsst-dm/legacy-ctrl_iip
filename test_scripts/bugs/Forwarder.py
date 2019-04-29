# FIXME: there are a number of errors in here, including uninitialized variables
from Scratchpad import Scratchpad
from toolsmod import get_timestamp
from toolsmod import get_epoch_timestamp
import yaml
import sys
import hashlib
import os.path
import os
import copy
import _thread
import pyfits
import np
from lsst.ctrl.iip.const import ACK_BOOL
from lsst.ctrl.iip.const import ACK_ID
from lsst.ctrl.iip.const import BASE_BROKER_ADDR
from lsst.ctrl.iip.const import CONSUME_QUEUE
from lsst.ctrl.iip.const import FORWARDER_JOB_PARAMS
from lsst.ctrl.iip.const import FORWARDER_HEALTH_CHECK
from lsst.ctrl.iip.const import FORWARDER_READOUT
from lsst.ctrl.iip.const import FQN
from lsst.ctrl.iip.const import HOSTNAME
from lsst.ctrl.iip.const import IP_ADDR
from lsst.ctrl.iip.const import JOB_NUM
from lsst.ctrl.iip.const import MSG_TYPE
from lsst.ctrl.iip.const import NAME
from lsst.ctrl.iip.const import PASSWD
from lsst.ctrl.iip.Consumer import Consumer
from lsst.ctrl.iip.SimplePublisher import SimplePublisher


class Forwarder:
    """Presents a vanilla L1 Forwarder personality. In
       nightly operation, at least 21 of these
       components will be available at any time (one for each raft).
    """

    def __init__(self):
        self._registered = False
        f = open('ForwarderCfg.yaml')
        # cfg data map...
        cdm = yaml.safe_load(f)
        try:
            self._name = cdm[NAME]
            self._passwd = cdm[PASSWD]
            self._fqn = cdm[FQN]
            self._base_broker_addr = cdm[BASE_BROKER_ADDR]
            self._consume_queue = cdm[CONSUME_QUEUE]
            # self._publish_queue = cdm[PUBLISH_QUEUE]
            self._hostname = cdm[HOSTNAME]
            self._ip_addr = cdm[IP_ADDR]
            self._DAQ_PATH = cdm['DAQ_PATH']
            # XXX FIX: Put in config file
            self.CHECKSUM_ENABLED = False
        except KeyError:
            print("Missing base keywords in yaml file... Bailing out...")
            sys.exit(99)

        self._home_dir = "/home/" + self._name + "/"
        self._base_broker_url = "amqp://%s:%s@%s" % (self._name, self._passwd, self._base_broker_addr)

        self._msg_actions = {FORWARDER_HEALTH_CHECK: self.process_health_check,
                             FORWARDER_JOB_PARAMS: self.process_job_params,
                             # Here if AR case needs different handler
                             'AR_FWDR_XFER_PARAMS': self.process_job_params,
                             'AR_FWDR_READOUT': self.process_foreman_readout,
                             FORWARDER_READOUT: self.process_foreman_readout}

        self.setup_publishers()
        self.setup_consumers()
        self._job_scratchpad = Scratchpad(self._base_broker_url)

    def setup_publishers(self):
        self._publisher = SimplePublisher(self._base_broker_url)

    def setup_consumers(self):
        threadname = "thread-" + self._consume_queue
        print("Threadname is %s" % threadname)

        self._consumer = Consumer(self._base_broker_url, self._consume_queue)
        try:
            _thread.start_new_thread(self.run_consumer, (threadname, 2,))
            print("Started Consumer Thread")
        except Exception:
            sys.exit(99)

    def run_consumer(self, threadname, delay):
        self._consumer.run(self.on_message)

    def on_message(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag)
        print("INcoming PARAMS, body is:\n%s" % body)
        msg_dict = body

        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)

    def process_health_check(self, params):
        self.send_ack_response("FORWARDER_HEALTH_CHECK_ACK", params)

    def process_job_params(self, params):
        """ The structure of the incoming job params is identical to the way job params
            are sent to prompt processing forwarders:
               MSG_TYPE: AR_FWDR_XFER_PARAMS
               JOB_NUM: .....
               ACK_ID: x1
               REPLY_QUEUE: .....
               FITS: FITS metadata someday?
               TRANSFER_PARAMS:
                   DISTRIBUTOR:
                       FQN: Name of entity receivine file
                       NAME: login name for receiving entity
                       HOSTNAME: Full host name for receiving entity
                       IP_ADDR: ip addr of archive
                       TARGET_DIR: Where to put file
                    ##  Below might be better as 'xfer_unit_list' for ccds or rafts, or other
                    CCD_LIST: for example...[1,2,3,7,10,14]
                    XFER_UNIT: CCD
                    FITS: FITS metadata someday?

              After the xfer params arrive, and ack is returned, we set up some short cut helpers, such as:
                 1) Make a filename stub for job that leaves out all but the CCD number
                 2) Put together the scp/bbftp string with login name and ip addr, plus target dir

        """
        job_params = copy.deepcopy(params)
        xfer_params = job_params['TRANSFER_PARAMS']

        # Also RM fits files in xfer_dir
        cmd = "rm " + self._DAQ_PATH + "*.fits"
        os.system(cmd)

        filename_stub = "%s_%s_%s_" % (job_params['JOB_NUM'], job_params['VISIT_ID'], job_params['IMAGE_ID'])

        login_str = "%s@%s:" % (xfer_params['DISTRIBUTOR']['NAME'], xfer_params['DISTRIBUTOR']['IP_ADDR'])

        target_dir = str(xfer_params['DISTRIBUTOR']['TARGET_DIR'])

        # xfer_params = transfer_params['XFER_PARAMS']
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

    def format2(self, job_num, raw_files_dict):
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
            cmd3 = 'echo ' + str(dte) + " >> " + target
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

    def send_ack_response(self, type, params):
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
        pass


if __name__ == "__main__":
    fwd = Forwarder()
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print("")
    print("Forwarder Finished")
