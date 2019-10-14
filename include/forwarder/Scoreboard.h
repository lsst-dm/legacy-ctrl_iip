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

#ifndef SCOREBOARD_H
#define SCOREBOARD_H

#include <iostream>
#include <map>
#include <set>
#include <memory>
#include "core/RedisConnection.h"

/**
 * Information used for readout transfer of fits file
 *
 * @param target location where fits file should go
 * @param session_id Current session ID
 * @param job_num Current running job
 * @param raft Raft number of the form "00"
 * @param ccds Name of ccds inside the raft to pull
 */
struct xfer_info { 
    std::string target;
    std::string session_id;
    std::string job_num;
    std::string raft;
    std::vector<std::string> ccds;
};

/**
 * Store information relating to readout details
 */
class Scoreboard {
    public:
        /**
         * Constuct Scoreboard
         *
         * @param host hostname of the redis server
         * @param port port number of redis server(usually 6379)
         * @param db_num database number to connect
         * @param password password to authenticate
         */
        Scoreboard(const std::string& host,
                   const int& port,
                   const int& db_num,
                   const std::string& password);

        /**
         * Destruct Scoreboard
         */
        ~Scoreboard();

        /**
         * Check if Image ID is ready to be assembled
         *
         * @param image_id Image ID
         * @return true if Image ID is ready to be assembled
         */
        bool is_ready(const std::string& image_id);

        /**
         * Add Image ID with Event name to keep track
         *
         * @param image_id Image ID
         * @param event custom event called `header_ready` and `end_readout`
         *      used for tracking if image is ready to be assembled
         */
        void add(const std::string& image_id, const std::string& event);

        /**
         * Remove Image from storage
         *
         * @param image_id Image ID
         *
         * @throws L1::KeyNotFound if Image ID does not exist in storage
         */
        void remove(const std::string& image_id);

        /**
         * Store transfer information
         *
         * @param image_id Image ID
         * @param xfer Transfer information
         */
        void add_xfer(const std::string&, const xfer_info&); 

        /**
         * Get transfer information
         *
         * @param image_id Image ID
         * @return transer info
         *
         * @throws L1::KeyNotFound if Image ID does not exist in storage
         */
        xfer_info get_xfer(const std::string&); 

        void set_fwd(const std::string& key, const std::string& body); 

    private:
        // RedisConnection
        std::unique_ptr<RedisConnection> _con;

        // map to store image id against events
        std::map<std::string, std::set<std::string>> _db;

        // map to store image id for transfer information
        std::map<std::string, xfer_info> _xfer;
};

#endif
