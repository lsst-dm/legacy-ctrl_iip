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

#include <signal.h>
#include <iostream>
#include <cstdio>

#include "core/Exceptions.h"
#include "core/Consumer.h"
#include "core/SimpleLogger.h"
#include "forwarder/miniforwarder.h"

namespace fs = boost::filesystem;

miniforwarder::miniforwarder() : IIPBase("ForwarderCfg.yaml", "Forwarder")
                                 , _hdr()
                                 , _daq("ats")
                                 , _fmt()
                                 , _db()
                                 , _sender() { 
    try { 
        const std::string user = _credentials->get_user("service_user");
        const std::string passwd = _credentials->get_user("service_passwd");
        const std::string ip_host = _config_root["BASE_BROKER_ADDR"].as<std::string>();
        const std::string header_dir = _config_root["HEADER_PATH"].as<std::string>();
        const std::string fits_dir = _config_root["FITS_PATH"].as<std::string>();

        _name = _config_root["NAME"].as<std::string>();
        _consume_q = _config_root["CONSUME_QUEUE"].as<std::string>();
        _amqp_url = "amqp://" + user + ":" + passwd + "@" + ip_host;

        _actions = {
            { "AT_FWDR_HEALTH_CHECK", bind(&miniforwarder::health_check, this, _1) },
            { "AT_FWDR_XFER_PARAMS", bind(&miniforwarder::xfer_params, this, _1) },
            { "AT_FWDR_HEADER_READY", bind(&miniforwarder::header_ready, this, _1) },
            { "AT_FWDR_END_READOUT", bind(&miniforwarder::end_readout, this, _1) }
        };

        _pub = new SimplePublisher(_amqp_url);

        _header_path = create_dir(header_dir);
        _fits_path = create_dir(fits_dir);
    }
    catch (L1::PublisherError& e) { exit(-1); }
    catch (L1::CannotCreateDir& e) { exit(-1); }
    catch (std::exception& e) { 
        LOG_CRT << e.what();
        exit(-1);
    }
}

miniforwarder::~miniforwarder() { 
    delete _pub;
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
        auto on_msg = bind(&miniforwarder::on_message, this, std::placeholders::_1);
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

        _db.add_xfer(image_id, xfer);
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
        _db.add(image_id, "header_ready");
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

        fs::path filepath = _fits_path / fs::path(image_id + ".fits");
        _daq.fetch(image_id, "00", "00", "WaveFront", filepath);

        _db.add(image_id, "end_readout");
        assemble(image_id);
        publish_ack(n);
    }
    catch (L1::CannotFetchPixel& e) { }
    catch (std::exception& e) { 
        LOG_CRT << e.what();
    }
}

void miniforwarder::publish_ack(const YAML::Node& n) { 
    try { 
        const std::string msg_type = n["MSG_TYPE"].as<std::string>();
        const std::string ack_id = n["ACK_ID"].as<std::string>();
        const std::string reply_q = n["REPLY_QUEUE"].as<std::string>();
        const std::string msg = _builder.build_ack(msg_type, _name, ack_id, "True");
        _pub->publish_message(reply_q, msg);
    }
    catch (L1::PublisherError& e) { }
    catch (std::exception& e) {
        LOG_CRT << e.what();
    }
}

void miniforwarder::assemble(const std::string& image_id) { 
    if (_db.is_ready(image_id)) { 
        const xfer_info xfer = _db.get_xfer(image_id);

        fs::path pix = _fits_path / fs::path(image_id + ".fits");
        fs::path header = _header_path / fs::path(image_id);
        fs::path to = fs::path(xfer.target) / fs::path(image_id + ".fits");

        try { 
            _fmt.write_header(pix, header);
            _sender.send(pix, to);
            LOG_INF << "********* READOUT COMPLETE for " << image_id;

            // clean up
            _db.remove(image_id);
            remove(pix.c_str());
            remove(header.c_str());
        } 
        catch (L1::CannotFormatFitsfile& e) { }
        catch (L1::CannotCopyFile& e) { } 
        catch (std::exception& e) { 
            std::string err = "Cannot assemble fitsfile because " + std::string(e.what());
            LOG_CRT << err; 
        }
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

void signal_handler(int signum) { 
    LOG_CRT << "Received CTRL-C";
    exit(-1);
}

int main() { 
    signal(SIGINT, signal_handler);
    miniforwarder fwd;
    fwd.run();
    return 0;
}
