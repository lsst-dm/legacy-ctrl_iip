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

#ifndef IIP_BASE_H
#define IIP_BASE_H

#include <memory>
#include <yaml-cpp/yaml.h>
#include "core/Credentials.h"

/**
 * Base class for CTRL_IIP package
 *
 * IIPBase handles loading of configuration files, setting up log file paths
 * and utility functions that are shared across objects.
 */
class IIPBase {
    public:
        /**
         * Construct IIPBase
         *
         * Loads configuration file, initializes log file and Credentials 
         * object for use with iip credentials needed for authentication.
         *
         * @param configfilename Name of configuration file to read
         * @param logfilename Name of log file to insert log statements
         *
         * @throws No exception thrown but application will `exit` if
         *      requirements are not met
         *
         * @exceptsafe Strong exception guarantee
         */
        IIPBase(const std::string& configfilename, const std::string& logfilename);

        /**
         * Destruct IIPBase
         */
        ~IIPBase();

        /**
         * Get the path to the log file
         *
         * Log file directory can be set multiple ways and this method returns
         * the final file path of the log file. `$IIP_CONFIG_DIR` environment
         * variable takes precendence over `LOGGING_DIR` (read from 
         * L1SystemCfg.yaml). If both of them are not set, log file will be
         * written to `/tmp`.
         *
         * @return log file path
         */
        std::string get_log_filepath();

        /**
         * Read configuration file
         * 
         * Load configuration file from `$IIP_CONFIG_DIR/{filename}` or 
         * `$CTRL_IIP_DIR/{filename}`. `$IIP_CONFIG_DIR takes precedence over
         * `$CTRL_IIP_DIR`.
         *
         * @param config_filename Name of configuration file
         * @return Root node of the YAML configuration file
         *
         * @throws No exception thrown but application will `exit` if 
         *      requirements are not met
         */
        std::string load_config_file(const std::string& config_filename);

        /**
         * Construct AMQP URL to RabbitMQ Server
         *      Example. `amqp://{username}:{password}@{broker_url}`
         * 
         * @param username RabbitMQ username
         * @param password RabbitMQ password
         * @param broker_url RabbitMQ hostname followed by vhost name
         *
         * @return RabbitMQ URL
         */
        std::string get_amqp_url(const std::string& username, 
                                 const std::string& password, 
                                 const std::string& broker_url);

    protected:
        // Root node of YAML configuration file
        YAML::Node _config_root;

        // Credential object instance
        std::unique_ptr<Credentials> _credentials;
};

#endif
