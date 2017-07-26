import pika
import os.path
import hashlib
import yaml
from Consumer import Consumer
from SimplePublisher import SimplePublisher
from const import *
import toolsmod  # here so reader knows where intake yaml method resides
from toolsmod import *
import thread
import logging
import ClusterJobScoreboard
import ClusterNodeScoreboard
import AckScoreboard
import traceback
import time

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class ClusterController:
    CLUSTER_CTRL_PUBLISH = "cluster_ctrl_publish"
    CLUSTER_CTRL_CONSUME = "cluster_ctrl_consume"
    ACK_PUBLISH = "cluster_ctrl_ack_publish"
    # AUDIT_CONSUME = "audit_consume"
    YAML = 'YAML'

    
    def __init__(self, filename=None):
        self._session_id = None
        self._name = "CLUSTER_CONTROLLER"
        self._config_file = 'L1SystemCfg.yaml'
	self._next_timed_ack_id = self.init_ack_id()
        if filename != None:
            self._config_file = filename

        cdm = toolsmod.intake_yaml_file(self._config_file)

        try:
            self._cluster_name = cdm[ROOT]['CLUSTER_BROKER_NAME']  # Message broker user/passwd for component
            self._cluster_passwd = cdm[ROOT]['CLUSTER_BROKER_PASSWD']
            self._ncsa_broker_addr = cdm[ROOT][NCSA_BROKER_ADDR]
            self._cluster_xfer_root = cdm[ROOT]['CLUSTER']['CLUSTER_XFER_ROOT']
            self._scbd_dict = cdm[ROOT]['SCOREBOARDS']
            self._cluster_node_dict = cdm[ROOT][XFER_COMPONENTS]['CLUSTER']['CLUSTER_NODES']
        except KeyError as e:
            raise L1Error(e)

	self._ncsa_msg_format = self.YAML

        if 'NCSA_MSG_FORMAT' in cdm[ROOT]:
            self._ncsa_msg_format = cdm[ROOT][NCSA_MSG_FORMAT]

        self._ncsa_broker_url = "amqp://" + self._cluster_name + ":" + self._cluster_passwd + "@" + str(self._ncsa_broker_addr)

        LOGGER.info('Building _ncsa_broker_url connection string for Cluster Controller. Result is %s',
                     self._ncsa_broker_url)

	# Create redis cluster node table and job table
	self.CLUSTER_JOB_SCBD = ClusterJobScoreboard.ClusterJobScoreboard('CLUSTER_JOB_SCBD', self._scbd_dict['CLUSTER_JOB_SCBD'])
        self.CLUSTER_NODE_SCBD = ClusterNodeScoreboard.ClusterNodeScoreboard('CLUSTER_NODE_SCBD', self._scbd_dict['CLUSTER_NODE_SCBD'], self._cluster_node_dict)
	self.CLUSTER_ACK_SCBD = AckScoreboard.AckScoreboard('CLUSTER_ACK_SCBD', self._scbd_dict['CLUSTER_ACK_SCBD'])

        self._msg_actions = { 'CLUSTER_RESOURCE_CHECK': self.process_resource_check,
			      'CLUSTER_HEALTH_CHECK_ACK': self.process_ack,
			      'READOUT': self.process_readout,
                              'NEXT_VISIT': self.process_next_visit,
			      'NEXT_VISIT_ACK': self.process_ack,
			      'READOUT_ACK': self.process_ack, 
			      'CLUSTER_RESOURCE_CHECK_ACK': self.process_ack,
			      'SEND_PARAMS_ACK': self.process_ack }

        self.setup_consumer()
        self.setup_publisher()

    
    def setup_consumer(self):
        LOGGER.info('Setting up consumers on %s', self._ncsa_broker_url)
        LOGGER.info('Running start_new_thread for consumer')

        self._cluster_consumer = Consumer(self._ncsa_broker_url, self.CLUSTER_CTRL_CONSUME, self._ncsa_msg_format)
        try:
            thread.start_new_thread( self.run_cluster_consumer, ("thread-cluster-consumer", 2,) )
        except:
            LOGGER.critical('Cannot start Cluster consumer thread, exiting...')
            raise L1Error

	self._ack_consumer = Consumer(self._ncsa_broker_url, self.ACK_PUBLISH, self._ncsa_msg_format)
	try:
	    thread.start_new_thread( self.run_ack_consumer, ("thread-ack-consumer", 2,) )
	except:
	    LOGGER.critical('Cannot start Cluster consumer thread, exiting...')
	    raise L1Error

    
    def run_cluster_consumer(self, threadname, delay):
        self._cluster_consumer.run(self.on_cluster_message)


    def run_ack_consumer(self, threadname, delay):
	self._ack_consumer.run(self.on_ack_message)


    def setup_publisher(self):
        LOGGER.info('Setting up Cluster publisher on %s using %s', self._ncsa_broker_url, self._ncsa_msg_format)
        self._cluster_publisher = SimplePublisher(self._ncsa_broker_url, self._ncsa_msg_format)


    def on_cluster_message(self, ch, method, properties, msg_dict):
        print "INCOMING On_cluster_message, msg is:\n%s" % msg_dict
        LOGGER.info('Message from Cluster callback message body is: %s', str(msg_dict))
        handler = self._msg_actions.get(msg_dict[MSG_TYPE])
        result = handler(msg_dict)


    def on_ack_message(self, ch, method, properties, msg_dict):
	print "INCOMING on_ack_message, msg is:\n%s" % msg_dict
	LOGGER.info('Message from Cluster callback message body is: %s', str(msg_dict))
	handler = self._msg_actions.get(msg_dict[MSG_TYPE])
	result = handler(msg_dict)


    def process_ack(self, params):
	self.CLUSTER_ACK_SCBD.add_timed_ack(params)	


    def process_next_visit(self, params):
        '''
            MSG_TYPE
            SESSION_ID
            VISIT_ID
            BORE_SIGHT
            ACK_ID
        '''
        self._cluster_consumer.run(self.on_cluster_message)


    def process_next_visit_ack(self, type, params):
        '''
            MSG_TYPE
            COMPONENT
            ACK_BOOL
            ACK_ID
        '''
        try:
            print("Storing visit and bore sight....")
            ack_id = params.get("ACK_ID")
            self._current_session_id = params.get("SESSION_ID")
            visit_id = params.get("VISIT_ID")
            bore_sight = params.get("BORE_SIGHT")

            # store visit id in job scoreboard
            self.CLUSTER_JOB_SCBD.store_visit_id(visit_id, bore_sight)
        except:
            traceback.print_exc()

        msg_params = {}
        msg_params[MSG_TYPE] = type
        msg_params['COMPONENT_NAME'] = self._name
        msg_params[ACK_BOOL] = True
        msg_params['ACK_ID'] = ack_id
        LOGGER.info('%s sent for ACK ID: %s', type, ack_id)
        self._cluster_publisher.publish_message(self.ACK_PUBLISH, msg_params)
        print("______FINISHED VISIT_ID STORE______")

    
    def process_resource_check(self, params):
        '''
           'MESSAGE_TYPE'
           'ACK_ID'
           'SESSION_ID'
           'BORE_SIGHT'
           'IMAGE_ID'
           'JOB_NUM'
           'CCD_LIST'
        '''
        # self.send_audit_message("received_")
        self.send_resource_ack_response("CLUSTER_RESOURCE_CHECK_ACK", params)


    def send_resource_ack_response(self, type, params):
        '''
            'MESSAGE_TYPE'
            'ACK_BOOL'
            'ACK_ID'
        '''
        try:
            print("Begin resource check")
            ack_id = params.get("ACK_ID")
            job_num = params.get("JOB_NUM")
	    self._current_session_id = params.get("SESSION_ID")
            ccd_list = params.get("CCD_LIST") # python dict with CCD as key and distributor_No as value
	    
            node_info = self.CLUSTER_NODE_SCBD.return_nodes_with_consume()
            # Check if there are enough available nodes
	    new_ack_id = self.get_next_timed_ack_id("CLUSTER_HEALTH_CHECK_ACK")
	    for node in node_info.keys():
		node_msg = {}
	        node_msg[MSG_TYPE] = "CLUSTER_HEALTH_CHECK"
	     	node_msg[ACK_ID] = new_ack_id
		self._cluster_publisher.publish_message(node_info[node],node_msg)
	    
	    time.sleep(5)
	    
	    ret_node = self.CLUSTER_ACK_SCBD.get_components_for_timed_ack(new_ack_id)
	    avail_node = []
            for component in ret_node.keys():
		if ret_node[component][ACK_BOOL] == True:
		    avail_node.append(component)

	    ret = False
	    if len(avail_node) >= len(ccd_list):
		ret = True
            	target_dir = self.construct_dir(params)
            	ret_dict = self.CLUSTER_JOB_SCBD.assign_job_to_node(ccd_list, avail_node, job_num, target_dir)
        except:
            if ack_id == None:
                LOGGER.info('%s failed, missing ACK_ID field', type)
                raise L1MessageError("Missing ACK_ID message param needed for send_ack_response")
            elif self._current_session_id == None:
                LOGGER.info('%s failed, missing SESSION_ID field', type)
                raise L1MessageError("Missing SESSION_ID param needed for send_ack_response")
            else:
                traceback.print_exc()
                LOGGER.info('Unknown error')
                raise L1MessageError("Unknown error")
        
	# Send resources needed for node 
	self.send_resource(ret_dict, ccd_list, params)
	
	# Send resource check ack
	msg_params = {}
        msg_params[MSG_TYPE] = type
        msg_params['COMPONENT_NAME'] = self._name
        msg_params[ACK_BOOL] = ret
        msg_params['ACK_ID'] = ack_id
        LOGGER.info('%s sent for ACK ID: %s', type, ack_id)
        self._cluster_publisher.publish_message(self.ACK_PUBLISH, msg_params)
        print("______FINISHED RESOURCE CHECK______")


    def send_resource(self, node_dict, ccd_list, params):
	node_info = self.CLUSTER_NODE_SCBD.return_nodes_with_consume()
	for node in node_dict.keys():
	    # Set node reserved
	    self.CLUSTER_NODE_SCBD.set_node_state(node, 'RESERVED')

	    # send message
            image_path = node_dict[node]['PATH_TO_FILE']
	    distributor = ccd_list[node_dict[node]['CCD_ID']]
	    ack_id = get_next_timed_ack_id("SEND_PARAMS_ACK")
            params_msg = {}
            params_msg[MSG_TYPE] = "SEND_PARAMS"
            params_msg['DISTRIBUTER'] = distributor
            params_msg['FILE_NAME'] = image_path
	    params_msg['ACK_ID'] = ack_id
	    params_msg['BORE_SIGHT'] = params['BORE_SIGHT']
	    params_msg['CCD_NUM'] = node_dict[node]['CCD_ID']
	    self._cluster_publisher.publish_message(node_info[node], params_msg)
    

    def process_readout(self, params):
        '''
            MSG_TYPE
            SESSION_ID
            JOB_NUM
            VISIT_ID
            IMAGE_ID
            ACK_ID
        '''
        # self.send_audit_message("received_")
        self.process_readout_ack("READOUT_ACK",params)

    
    def process_readout_ack(self, type, params):
        '''
            MSG_TYPE
            SESSION_ID
            JOB_NUM
            IMAGE_ID
            RESULT_SET
            ACK_ID
            COMPONENT
        '''
        self._current_session_id = params['SESSION_ID']
        job = params['JOB_NUM']
        visit = params['VISIT_ID']
        image = params['IMAGE_ID']
	
        # Use job id to check the status of every node that dealing with CCD in this job
        result_set = self.CLUSTER_JOB_SCBD.check_job_status(job, self.CLUSTER_NODE_SCBD)

        ack_params = {}
        ack_params[MSG_TYPE] = 'READOUT_ACK'
        ack_params['ACK_ID'] = params['ACK_ID']
        ack_params['JOB_NUM'] = job
        ack_params['IMAGE_ID'] = image
        ack_params['RESULT_SET'] = result_set
        ack_params['COMPONENT_NAME'] = self._name

        print("______Job %s finished checking_____") % job
        print(result_set)
        self._cluster_publisher.publish_message(self.ACK_PUBLISH, ack_params)

    
    def send_audit_message(self, prefix, params):
        audit_params = {}
        audit_params['SUB_TYPE'] = str(prefix) + str(params['MSG_TYPE']) + "_msg"
        audit_params['DATA_TYPE'] = self._name
        audit_params['TIME'] = get_epoch_timestamp()
        self._archive_publisher.publish_message(self.AUDIT_CONSUME, audit_params)

    
    def construct_dir(self, params):
        image = params['IMAGE_ID']
        ack_id = params['ACK_ID']

        target_dir_visit = self._cluster_xfer_root + "/"
        target_dir_image = self._cluster_xfer_root + "/" + str(image) + "/"

        '''
        if os.path.isdir(target_dir_visit):
            pass
        else:
            os.mkdir(target_dir_visit, 0766)

        if os.path.isdir(target_dir_image):
            pass
        else:
            os.mkdir(target_dir_image, 0766)
        '''
        return target_dir_image


    def get_next_timed_ack_id(self, ack_type):
        self._next_timed_ack_id = self._next_timed_ack_id + 1
	val = {}
	val['CURRENT_ACK_ID'] = self._next_timed_ack_id
	toolsmod.export_yaml_file(self.cluster_ack_id_file, val)
	retval = ack_type + "_" + str(self._next_timed_ack_id).zfill(6)
	return retval


    def init_ack_id(self):
        if os.path.isfile(self.cluster_ack_id_file):
            val = toolsmod.intake_yaml_file(self.cluster_ack_id_file)
            current_id = val['CURRENT_ACK_ID'] + 1
            if current_id > 999900:
                current_id = 1
            val['CURRENT_ACK_ID'] = current_id
            toolsmod.export_yaml_file(self.cluster_ack_id_file, val)
            return current_id
        else:
            current_id = 1
            val = {}
            val['CURRENT_ACK_ID'] = current_id
            toolsmod.export_yaml_file(self.cluster_ack_id_file, val)
            return current_id


def main():
    logging.basicConfig(filename='logs/NCSAForeman.log', level=logging.INFO, format=LOG_FORMAT)
    a_c = ClusterController()
    print "Beginning ClusterController event loop..."
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass

    print ""
    print "Cluster Controller Done."

if __name__ == "__main__": main()

