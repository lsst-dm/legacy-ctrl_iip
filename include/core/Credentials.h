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

#ifndef CREDENTIALS_H
#define CREDENTIALS_H

#include <iostream>
#include <yaml-cpp/yaml.h>

/**
 * Credential object for CTRL_IIP package authentication
 */
class Credentials {
    public: 
        /**
         * Constructs Credential
         *
         * Loads secure file to read auth credentials
         *
         * @param filename secure file name
         * @throws No exception thrown but application will `exit` if 
         *      secure file is not found
         */
        Credentials(const std::string& filename);

        /**
         * Utility function for loading secure authentication file
         *
         * @param filename secure file name
         * @return Root node of secure file
         * @throws No exception thrown but application will `exit` if 
         *      secure file is not found
         */
        YAML::Node load_secure_file(const std::string& filename);

        /**
         * Get username from secure file
         *
         * @param user_alias RabbitMQ user alias
         * @return RabbitMQ username
         *
         * @throws No exception thrown but application will `exit` if 
         *      user alias key does not exist in secure file
         */
        std::string get_user(const std::string& user_alias);

        /**
         * Get password from secure file
         *
         * @param passwd_alias RabbitMQ passwd alias
         * @return RabbitMQ password
         *
         * @throws No exception thrown but application will `exit` if 
         *      password alias key does not exist in secure file
         */
        std::string get_passwd(const std::string& passwd_alias);

    private:
        // Root node of secure file
        YAML::Node _credentials;
};

#endif
