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

#define BOOST_LOG_DYN_LINK 1

#include <iostream>
#include "core/SimpleLogger.h"
#include "core/IIPBase.h"

IIPBase::IIPBase(const std::string& configfilename, const std::string& logfilename) {
    _config_root = load_config_file(configfilename);
    init_log(get_log_filepath(), logfilename);

    _credentials = new Credentials("iip_cred.yaml");
}

IIPBase::~IIPBase() { 
    delete _credentials;
}

std::string IIPBase::get_log_filepath() { 
    char* iip_log_dir = getenv("IIP_LOG_DIR");
    YAML::Node log_node = _config_root["LOGGING_DIR"];

    std::string path;
    if (iip_log_dir) { 
        path = iip_log_dir;    
    }
    else if (log_node) { 
        path = log_node.as<std::string>();
    }
    else { 
        path = "/tmp";
    }

    std::cout << "Log filepath is located at " << path << std::endl;
    return path;
}

YAML::Node IIPBase::load_config_file(const std::string& config_filename) { 
    char* iip_config_dir = getenv("IIP_CONFIG_DIR");
    char* ctrl_iip_dir = getenv("CTRL_IIP_DIR");

    if (!iip_config_dir && !ctrl_iip_dir) { 
        std::cout << "Please set environment variable CTRL_IIP_DIR or IIP_CONFIG_DIR" << std::endl;
        exit(-1);
    }

    std::string config_file;
    if (iip_config_dir) { 
        std::string config_dir(iip_config_dir); 
        config_file = config_dir + "/" + config_filename;
    }
    else if (ctrl_iip_dir) { 
        std::string config_dir(ctrl_iip_dir); 
        config_file = config_dir + "/etc/config/" + config_filename;
    }
    else {
        std::cout << "Cannot find configuration file " << config_filename << std::endl;
	exit(-1); 
    }
    std::cout << "Loaded configuration from " << config_file << std::endl;
       
    try { 
        return YAML::LoadFile(config_file)["ROOT"];
    }
    catch (YAML::BadFile& e) { 
        std::cout << "Cannot read configuration file " << config_filename << std::endl;
        exit(-1); 
    }  
}

std::string IIPBase::get_amqp_url(const std::string& username, 
                                  const std::string& passwd, 
                                  const std::string& broker_url) { 
    std::ostringstream base_broker_url; 
    base_broker_url << "amqp://" \
        << username << ":" \
        << passwd << "@" \
        << broker_url;
    std::string url = base_broker_url.str();
    std::cout << "Constructed amqp connection to " << broker_url << std::endl;
    return url;
}
