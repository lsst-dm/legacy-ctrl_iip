#include <signal.h>
#include <iostream>

#include "core/Exceptions.h"
#include "core/Consumer.h"
#include "core/SimpleLogger.h"
#include "forwarder/miniforwarder.h"

using namespace std;
using namespace YAML;
using namespace L1;
using namespace boost::filesystem;

miniforwarder::miniforwarder() : IIPBase("ForwarderCfg.yaml", "Forwarder")
                                 , _hdr()
                                 , _daq("ats", "_something")
                                 , _fmt()
                                 , _db()
                                 , _sender() { 
    try { 
        const string user = credentials->get_user("service_user");
        const string passwd = credentials->get_user("service_passwd");
        const string ip_host = config_root["BASE_BROKER_ADDR"].as<string>();
        const string work_dir = config_root["WORK_DIR"].as<string>();

        _name = config_root["NAME"].as<string>();
        _consume_q = config_root["CONSUME_QUEUE"].as<string>();
        _amqp_url = "amqp://" + user + ":" + passwd + "@" + ip_host;

        _actions = {
            { "AT_FWDR_HEALTH_CHECK", bind(&miniforwarder::health_check, this, _1) },
            { "AT_FWDR_XFER_PARAMS", bind(&miniforwarder::xfer_params, this, _1) },
            { "AT_FWDR_HEADER_READY", bind(&miniforwarder::header_ready, this, _1) },
            { "AT_FWDR_END_READOUT", bind(&miniforwarder::end_readout, this, _1) }
        };

        _pub = new SimplePublisher(_amqp_url);

        _header_path = create_dir(work_dir, "header");
        _fits_path = create_dir(work_dir, "source");
    }
    catch (CannotCreateDir& e) {
        LOG_CRT << e.what();
        exit(-1);
    }
    catch (exception& e) { 
        LOG_CRT << e.what();
        exit(-1);
    }
}

miniforwarder::~miniforwarder() { 
    delete _pub;
}

void miniforwarder::on_message(const string& message) { 
    try {
        LOG_DBG << "Received message " << message;
        const Node n = Load(message);
        const string message_type = n["MSG_TYPE"].as<string>();
        _actions[message_type](n);
    }
    catch(exception& e) {
        LOG_CRT << e.what();
    }
}

void miniforwarder::run() { 
    Consumer consumer(_amqp_url, _consume_q);
    auto on_msg = bind(&miniforwarder::on_message, this, placeholders::_1);
    consumer.run(on_msg);
}

void miniforwarder::health_check(const Node& n) { 
    publish_ack(n);
}

void miniforwarder::xfer_params(const Node& n) {
    try { 
        // BAD MEMBER VARIABLE
        _target = n["TARGET_LOCATION"].as<string>();
       
        const string image_id = n["IMAGE_ID"].as<string>();
        _db.init(image_id); 

        publish_ack(n);
    }
    catch (exception& e) { 
        LOG_CRT << e.what();
    }
}

void miniforwarder::header_ready(const Node& n) {
    try { 
        const string filename = n["FILENAME"].as<string>();
        const string image_id = n["IMAGE_ID"].as<string>();
        const string reply_q = n["REPLY_QUEUE"].as<string>();
        const string ack_id = n["ACK_ID"].as<string>();

        path header = _header_path / path(image_id);
        _hdr.fetch(filename, header);
        _db.add(image_id, "header_ready");
        assemble(image_id);
        publish_ack(n);
    }
    catch (exception& e) { 
        LOG_CRT << e.what();
    }
}

void miniforwarder::end_readout(const Node& n) {
    try { 
        const string image_id = n["IMAGE_ID"].as<string>();

        /** TODO: these should be dynamic information from CSC **/
        const string raft = "22";
        const string board_type = "Science";
        vector<string> ccds { 
            "00", "01", "02", "10", "11", "12", "20", "21", "22"
        };

        // for (auto& ccd : ccds) { 
            //string filename = image_id + "--" + "R" + raft + "S" + ccd;
            string filename = image_id + "--" + "R" + raft + "S00";
            path filepath = _fits_path / path(filename);
            //_daq.fetch(image_id, raft, ccd, board_type, filepath);
            _daq.fetch(image_id, "00", "00", "WaveFront", filepath);
        // }

        /**
        path filepath = _fits_path / path(image_id);
        _daq.fetch(image_id, "00", "00", "WaveFront", filepath);

        _db.add(image_id, "end_readout");
        assemble(image_id);
        publish_ack(n);
        */
    }
    catch (exception& e) { 
        LOG_CRT << e.what();
    }
}

void miniforwarder::publish_ack(const Node& n) { 
    try { 
        const string msg_type = n["MSG_TYPE"].as<string>();
        const string ack_id = n["ACK_ID"].as<string>();
        const string reply_q = n["REPLY_QUEUE"].as<string>();
        const char* msg = _builder.build_ack(msg_type, _name, ack_id, "True");
        _pub->publish_message(reply_q, msg);
    }
    catch (exception& e) {
        LOG_CRT << e.what();
    }
}

void miniforwarder::assemble(const string& image_id) { 
    if (_db.is_ready(image_id)) { 
        path pix = _fits_path / path(image_id);
        path header = _header_path / path(image_id);
        path to = path(_target) / path(image_id);

        _fmt.write_header(pix, header);
        _sender.send(pix, to);  // this target is the bad boy
        _db.remove(image_id);
        LOG_INF << image_id << " readout complete.";
    }
}

path miniforwarder::create_dir(const string& root, const string& dir) { 
    path root_dir(root);
    path file_path = root_dir / path(dir);

    boost::system::error_code err;
    bool status = create_directories(file_path, err);

    if (err.value()) {
        throw CannotCreateDir("Cannot create directory for path " 
                + file_path.string() + " because " + err.message());
    }
    return file_path;
}

void signal_handler(int signum) { 
    LOG_CRT << "Received CTRL-C";
    exit(1);
}

int main() { 
    signal(SIGINT, signal_handler);
    miniforwarder fwd;
    fwd.run();
}
