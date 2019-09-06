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

/**
 * Information used for readout transfer of fits file
 *
 * @param target location where fits file should go
 */
struct xfer_info { 
    std::string target;
};

/**
 * Store information relating to readout details
 */
class Scoreboard {
    public:
        /**
         * Constuct Scoreboard
         */
        Scoreboard();

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

    private:
        // map to store image id against events
        std::map<std::string, std::set<std::string>> _db;

        // map to store image id for transfer information
        std::map<std::string, xfer_info> _xfer;
};

#endif
