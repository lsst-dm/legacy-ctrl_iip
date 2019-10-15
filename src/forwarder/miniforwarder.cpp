/*
 * This file is part of ctrl_iip
 *
 * Developed for the LSST Data Management System.
 * This product includes software developed by the LSST Project
 * (https://www.lsst.org).
 * See the COPYRIGHT file at the top-level directory of this distribution
 * for details of code ownership.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include <iostream>
#include <cstdio>
#include <unistd.h> // gethostname
#include <netdb.h>

#include "core/Exceptions.h"
#include "core/Consumer.h"
#include "core/SimpleLogger.h"
#include "forwarder/miniforwarder.h"

namespace fs = boost::filesystem;

miniforwarder::miniforwarder(const std::string& config, 
                             const std::string& log) : IIPBase(config, log)
                                 , _hdr()
                                 , _fmt()
                                 , _readoutpattern(_config_root)
                                 , _sender() { 
    try { 
        // rabbitmq configuration
        const std::string user = _credentials->get_user("service_user");
        const std::string passwd = _credentials->get_user("service_passwd");
        const std::string ip_host = _config_root["BASE_BROKER_ADDR"].as<std::string>();
        _consume_q = _config_root["CONSUME_QUEUE"].as<std::string>();
        _archive_q = _config_root["ARCHIVE_QUEUE"].as<std::string>();

        // cfitsio configuration
        const std::string header_dir = _config_root["HEADER_PATH"].as<std::string>();
        const std::string fits_dir = _config_root["FITS_PATH"].as<std::string>();

        // redis configuration
        const std::string redis_host = _config_root["REDIS_HOST"].as<std::string>();
        const int redis_port = _config_root["REDIS_PORT"].as<int>();
        const int redis_db = _config_root["REDIS_DB"].as<int>();
        const std::string redis_pwd = "meh"; // should come from credentials

        // heartbeat configuration
        _set_timeout = _config_root["SET_TIMEOUT"].as<int>();
        _check_timeout = _config_root["CHECK_TIMEOUT"].as<int>();

        // daq configuration
        _partition = _config_root["PARTITION"].as<std::string>();
        _daq_locations = _config_root[_partition].as<std::vector<std::string>>();

        _name = _config_root["NAME"].as<std::string>();
        _amqp_url = "amqp://" + user + ":" + passwd + "@" + ip_host;

        _actions = {
            { "AT_FWDR_HEALTH_CHECK", std::bind(&miniforwarder::health_check, this, std::placeholders::_1) },
            { "AT_FWDR_XFER_PARAMS", std::bind(&miniforwarder::xfer_params, this, std::placeholders::_1) },
            { "AT_FWDR_HEADER_READY", std::bind(&miniforwarder::header_ready, this, std::placeholders::_1) },
            { "AT_FWDR_END_READOUT", std::bind(&miniforwarder::end_readout, this, std::placeholders::_1) },
            { "FILE_TRANSFER_COMPLETED_ACK", std::bind(&miniforwarder::process_ack, this, std::placeholders::_1) },
            { "ASSOCIATED", std::bind(&miniforwarder::associated, this, std::placeholders::_1) }
        };

        _pub = std::unique_ptr<SimplePublisher>(new SimplePublisher(_amqp_url));
        _db = std::unique_ptr<Scoreboard>(
                new Scoreboard(redis_host, redis_port, redis_db, redis_pwd));
        _daq = std::unique_ptr<DAQFetcher>(new DAQFetcher(_partition.c_str()));

        _header_path = create_dir(header_dir);
        _fits_path = create_dir(fits_dir);

        _forwarder_list = "forwarder_list";
        _association_key = "f99_association";
        
        auto bound_register_fwd = std::bind(&miniforwarder::register_fwd, this); 
        _hb_params.timeout = _set_timeout;
        _hb_params.key = _association_key;
        _hb_params.redis_host = redis_host;
        _hb_params.redis_port = redis_port;
        _hb_params.redis_db = redis_db;
        _hb_params.action = bound_register_fwd;

        register_fwd();

        _beacon = std::unique_ptr<Beacon>(new Beacon(_hb_params));
        _watcher = std::unique_ptr<Watcher>(new Watcher());
    }
    catch (L1::PublisherError& e) { exit(-1); }
    catch (L1::CannotCreateDir& e) { exit(-1); }
    catch (std::exception& e) { 
        LOG_CRT << e.what();
        exit(-1);
    }
}

miniforwarder::~miniforwarder() { 
}

void miniforwarder::on_message(const std::string& message) { 
    try {
        LOG_DBG << "Received message " << message;
        const YAML::Node n = YAML::Load(message);
        const std::string message_type = n["MSG_TYPE"].as<std::string>();
        _actions[message_type](n);
    }
    catch(std::exception& e) {
        LOG_CRT << e.what();
    }
}

void miniforwarder::run() { 
    try { 
        Consumer consumer(_amqp_url, _consume_q);
        auto on_msg = bind(&miniforwarder::on_message, this, 
                std::placeholders::_1);
        consumer.run(on_msg);
    } 
    catch (L1::ConsumerError& e) { exit(-1); }
    catch (std::exception& e) { 
        LOG_CRT << e.what();
        exit(-1);
    }
}

void miniforwarder::health_check(const YAML::Node& n) { 
    publish_ack(n);
}

void miniforwarder::xfer_params(const YAML::Node& n) {
    try { 
        const std::string image_id = n["IMAGE_ID"].as<std::string>();
        xfer_info xfer;
        xfer.target = n["TARGET_LOCATION"].as<std::string>();
        xfer.session_id = n["SESSION_ID"].as<std::string>();
        xfer.job_num = n["JOB_NUM"].as<std::string>();

        const YAML::Node params = n["XFER_PARAMS"];
        xfer.raft = params["RAFT_LIST"].as<std::string>();
        xfer.ccds = params["RAFT_CCD_LIST"].as<std::vector<std::string>>();

        _db->add_xfer(image_id, xfer);
        publish_ack(n);
    }
    catch (std::exception& e) { 
        LOG_CRT << e.what();
    }
}

void miniforwarder::header_ready(const YAML::Node& n) {
    try { 
        const std::string filename = n["FILENAME"].as<std::string>();
        const std::string image_id = n["IMAGE_ID"].as<std::string>();
        const std::string reply_q = n["REPLY_QUEUE"].as<std::string>();
        const std::string ack_id = n["ACK_ID"].as<std::string>();

        fs::path header = _header_path / fs::path(image_id);
        _hdr.fetch(filename, header);
        _db->add(image_id, "header_ready");
        assemble(image_id);
        publish_ack(n);
    }
    catch (L1::CannotFetchHeader& e) { }
    catch (std::exception& e) { 
        LOG_CRT << e.what();
    }
}

void miniforwarder::end_readout(const YAML::Node& n) {
    try { 
        const std::string image_id = n["IMAGE_ID"].as<std::string>();
        const xfer_info xfer = _db->get_xfer(image_id);
        const std::string raft = xfer.raft;
        const std::vector<std::string> ccds = xfer.ccds;

        for (auto& ccd : ccds) { 
            const std::string filename = image_id + "--R" + raft + "S" + ccd + ".fits";
            const fs::path filepath = _fits_path / fs::path(filename);
            if (!check_valid_board(raft, ccd)) { 
                std::string err = "Raft/ccd " + raft + "/" + ccd + 
                    " does not exist in partition " + _partition;
                LOG_CRT << err;
                throw L1::CannotFetchPixel(err);
            }
            _daq->fetch(image_id, raft, ccd, "WaveFront", filepath);
        }

        _db->add(image_id, "end_readout");
        assemble(image_id);
        publish_ack(n);
    }
    catch (L1::KeyNotFound& e) { }
    catch (L1::CannotFetchPixel& e) { }
    catch (std::exception& e) { 
        LOG_CRT << e.what();
    }
}

void miniforwarder::process_ack(const YAML::Node& n) { 
    try { 
        const std::string msg_type = n["MSG_TYPE"].as<std::string>();
        LOG_INF << "Got ack for message type " << msg_type;
    }
    catch (std::exception& e) { 
        LOG_CRT << e.what();
    }
}

void miniforwarder::associated(const YAML::Node& n) {
    try { 
        const std::string key = n["ASSOCIATION_KEY"].as<std::string>();
        const std::string reply_q = n["REPLY_QUEUE"].as<std::string>();
        const std::string msg = _builder.build_associated_ack(_association_key);

        _pub->publish_message(reply_q, msg);

        heartbeat_params params = _hb_params;
        params.timeout = _check_timeout;
        params.key = key;
        _watcher->start(params);
    }
    catch(std::exception& e) { 
        LOG_CRT << e.what();
    }
}

void miniforwarder::publish_ack(const YAML::Node& n) { 
    try { 
        const std::string msg_type = n["MSG_TYPE"].as<std::string>();
        const std::string ack_id = n["ACK_ID"].as<std::string>();
        const std::string reply_q = n["REPLY_QUEUE"].as<std::string>();
        const std::string msg = _builder.build_ack(msg_type, _name, 
                ack_id, "True");
        _pub->publish_message(reply_q, msg);
    }
    catch (L1::PublisherError& e) { }
    catch (std::exception& e) {
        LOG_CRT << e.what();
    }
}

void miniforwarder::publish_xfer_complete(const std::string& to,
                                          const std::string& session_id,
                                          const std::string& job_num) {
    try { 
        const std::string filename = to.substr(to.find(":") + 1);
        const std::string msg = _builder.build_xfer_complete(filename, 
                session_id, job_num, _consume_q);
        _pub->publish_message(_archive_q, msg);
    }
    catch (L1::PublisherError& e) { }
    catch (std::exception& e) {
        LOG_CRT << e.what();
    }
}

void miniforwarder::assemble(const std::string& image_id) { 
    try { 
        if (_db->is_ready(image_id)) { 
            const xfer_info xfer = _db->get_xfer(image_id);
            const std::string raft = xfer.raft;
            const std::vector<std::string> ccds = xfer.ccds;
            const std::string session_id = xfer.session_id;
            const std::string job_num = xfer.job_num;
            const fs::path header = _header_path / fs::path(image_id);

            for (auto& ccd : ccds) { 
                const std::string filename = image_id + "--R" + raft + "S" + ccd + ".fits";
                const fs::path pix = _fits_path / fs::path(filename);
                const fs::path to = fs::path(xfer.target) / fs::path(filename);

                std::vector<std::string> pattern = _readoutpattern.pattern("WFS");
                _fmt.write_header(pattern, pix, header);
                _sender.send(pix, to);
                publish_xfer_complete(to.string(), session_id, job_num);
                
                LOG_INF << "********* READOUT COMPLETE for " << image_id;

                _db->remove(image_id);
                std::remove(pix.c_str());
            }

            std::remove(header.c_str());
        }
    }
    catch (L1::KeyNotFound& e) { }
    catch (L1::InvalidReadoutPattern& e) { }
    catch (L1::CannotFormatFitsfile& e) { }
    catch (L1::CannotCopyFile& e) { } 
    catch (std::exception& e) { 
        std::string err = "Cannot assemble fitsfile because " + 
            std::string(e.what());
        LOG_CRT << err; 
    }
}

fs::path miniforwarder::create_dir(const std::string& root) { 
    fs::path file_path(root);

    boost::system::error_code err;
    bool status = create_directories(file_path, err);

    if (err.value()) {
        std::string err_msg = "Cannot create directory for path " 
                + file_path.string() + " because " + err.message();
        LOG_CRT << err_msg;
        throw L1::CannotCreateDir(err_msg);
    }
    return file_path;
}

void miniforwarder::register_fwd() { 
    char hostname[HOST_NAME_MAX];
    gethostname(hostname, HOST_NAME_MAX);

    struct addrinfo addr;
    struct addrinfo *infoptr = NULL;
    addr.ai_family = AF_INET;
    // TODO: RAII
    int response = getaddrinfo(hostname, NULL, NULL, &infoptr);
    if (response) { 
        LOG_CRT << "Cannot get hostname";
        throw L1::L1Exception("Cannot get hostname");
    }

    struct addrinfo *p;
    char host[256];
    std::string ip_addr;
    for (p = infoptr; p != NULL; p = p->ai_next) { 
        getnameinfo(p->ai_addr, p->ai_addrlen, host, sizeof(host), NULL, 0, 
                NI_NUMERICHOST);
        ip_addr = host;
        break;
    }
    freeaddrinfo(infoptr);

    const std::string msg = _builder.build_fwd_info(hostname, ip_addr, _consume_q);
    _db->set_fwd(_forwarder_list, msg);
    LOG_INF << "Set forwarder in redis list";
}

bool miniforwarder::check_valid_board(const std::string& raft, 
                                      const std::string& ccd) {
    const std::string bay_board = raft + "/" + ccd[0]; 
    auto found = std::find(_daq_locations.begin(), _daq_locations.end(), 
            bay_board);
    if (found == _daq_locations.end()) { 
        return false;
    }
    return true;
}
