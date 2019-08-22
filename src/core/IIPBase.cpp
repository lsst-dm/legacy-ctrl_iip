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

#include "core/IIPBase.h"

using namespace std; 
using namespace YAML;

IIPBase::IIPBase(string configfilename, string logfilename) {
    // Read environment variables
    this->iip_config_dir = getenv("IIP_CONFIG_DIR");
    this->iip_log_dir = getenv("IIP_LOG_DIR");
    this->ctrl_iip_dir = getenv("CTRL_IIP_DIR");

    // Read config file
    this->config_root = load_config_file(configfilename);
    init_log(this->get_log_filepath(), logfilename);

    this->credentials = new Credentials("iip_cred.yaml");
    LOG_DBG << "Base constructor complete";
}

string IIPBase::get_log_filepath() { 
    string path;
    Node log_node = this->config_root["LOGGING_DIR"];
    if (this->iip_log_dir) { 
        path = this->iip_log_dir;    
    }
    else if (log_node) { 
        path = log_node.as<string>();
    }
    else { 
        path = "/tmp";
    }

    cout << "Log filepath is " << path << endl;
    return path;
}

Node IIPBase::load_config_file(string config_filename) { 
    if (!this->iip_config_dir && !this->ctrl_iip_dir) { 
        cout << "Please set environment variable CTRL_IIP_DIR or IIP_CONFIG_DIR" << endl;
        exit(-1);
    }

    string config_file;
    if (this->iip_config_dir) { 
        string config_dir(this->iip_config_dir); 
        config_file = config_dir + "/" + config_filename;
    }
    else if (this->ctrl_iip_dir) { 
        string config_dir(this->ctrl_iip_dir); 
        config_file = config_dir + "/etc/config/" + config_filename;
    }
    else {
        cout << "Cannot find configuration file " << config_filename << endl;
	exit(-1); 
    }
    cout << "Loaded configuration from " << config_file << endl;
       
    try { 
        return LoadFile(config_file)["ROOT"];
    }
    catch (BadFile& e) { 
        cout << "Cannot read configuration file " << config_filename << endl;
        exit(-1); 
    }  
}

string IIPBase::get_amqp_url(string username, string passwd, string broker_url) { 
    ostringstream base_broker_url; 
    base_broker_url << "amqp://" \
        << username << ":" \
        << passwd << "@" \
        << broker_url;
    string url = base_broker_url.str();
    LOG_DBG << "Constructed amqp connection to " << broker_url; 
    return url;
}
