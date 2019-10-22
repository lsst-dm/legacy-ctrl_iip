/*
 * This file is part of dm_forwarder
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

#include <boost/filesystem.hpp>
#include "core/Credentials.h"
#include "core/SimpleLogger.h"

namespace fs = boost::filesystem;

Credentials::Credentials(const std::string& filename) { 
    _credentials = load_secure_file(filename);
}

YAML::Node Credentials::load_secure_file(const std::string& filename) { 
    fs::path home = std::string(getenv("HOME"));
    fs::path dirpath = home / fs::path(".lsst");
    fs::path filepath = home / fs::path(".lsst") / fs::path(filename);

    if (!fs::exists(filepath)) { 
        std::ostringstream message;
        message << "Secure file " << filename << " doesn't exist.";
        std::cout << message.str() << std::endl;
        LOG_CRT << message.str();
        exit(-1);
    }

    fs::perms dirperm = fs::status(dirpath).permissions();
    fs::perms fileperm = fs::status(filepath).permissions();

    if (dirperm != fs::owner_all) { 
        std::ostringstream message;
        message <<  "Directory " << dirpath << " is not secure.";
        std::cout << message.str() << std::endl;
        std::cout << "Please run `chmod 700 " << dirpath << "` to fix it." << std::endl;
        LOG_CRT << message.str();
        exit(-1);
    }
    if (fileperm != (fs::owner_read | fs::owner_write)) { 
        std::ostringstream message;
        message << "File " << filepath << " is not secure.";
        std::cout << message.str() << std::endl;
        std::cout << "Please run `chmod 600 " << filepath << "` to fix it." << std::endl;
        LOG_CRT << message.str();
        exit(-1);
    }

    LOG_INF << "Loaded secure file from " << filepath;
    try { 
        return YAML::LoadFile(filepath.string());
    }
    catch (YAML::BadFile& e) { 
        LOG_CRT << "Cannot read secure file " << filepath;
        exit(-1); 
    }  
}

std::string Credentials::get_user(const std::string& user_alias) { 
    try { 
        std::string user = _credentials["rabbitmq_users"][user_alias].as<std::string>();
        return user;
    }
    catch (YAML::TypedBadConversion<std::string>& e) { 
	LOG_CRT  << "Cannot read rabbitmq username from secure file";
	exit(-1); 
    }
}

std::string Credentials::get_passwd(const std::string& passwd_alias) { 
    try { 
        std::string passwd = _credentials["rabbitmq_users"][passwd_alias].as<std::string>();
        return passwd;
    }
    catch (YAML::TypedBadConversion<std::string>& e) { 
	LOG_CRT << "Cannot read rabbitmq password from secure file";
	exit(-1); 
    }
}
