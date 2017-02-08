import sys, getopt
import pika 

queue_list = [
            "ar_foreman_consume",
            "pp_foreman_consume",
            "cu_foreman_consume",
            "dmcs_consume",
            "dmcs_ack_consume",
            "ocs_dmcs_consume",
            "event_dmcs_consume",
            "dmcs_ocs_publish",
            "ar_forwarder_publish",
            "pp_forwarder_publish",
            "cu_forwarder_publish",
            "f1_consume",
            "d1_consume",
            "ar_foreman_ack_publish",
            "pp_foreman_ack_publish",
            "cu_foreman_ack_publish",
            "audit_consume",
            "archive_ctrl_consume",
            "archive_ctrl_publish",
            "ncsa_consume",
            "ncsa_publish"]

connection = pika.BlockingConnection(pika.URLParameters("amqp://BASE:BASE@141.142.208.241:5672/%2fbunny"))
channel = connection.channel()

def setup_q(): 
    for q in queue_list: 
        channel.queue_declare(q)
        channel.queue_bind(q, "message")    

def purge_q(): 
    for q in queue_list:
        channel.queue_purge(q)

def main(argv): 
    opts, args = getopt.getopt(argv, "", ["declare=", "purge"])
    for opt, arg in opts: 
        if opt in ("--declare"): 
            print "SETTING UP"
            setup_q()
        elif opt in ("--purge"):
            print "PURGING Q"
            purge_q()
        
if __name__ == "__main__": main(sys.argv[1:]) 
