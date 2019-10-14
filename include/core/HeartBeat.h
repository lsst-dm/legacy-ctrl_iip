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

#ifndef HEARTBEAT_H
#define HEARTBEAT_H

#include <atomic>
#include <functional>
#include <mutex>
#include <condition_variable>

struct heartbeat_params { 
    std::string redis_host;
    int redis_port;
    int redis_db;

    std::string key;
    int timeout;
    std::function<void ()> action;
};

class Watcher { 
    public:
        void start(const heartbeat_params params); 
        void clear();

    private:
        std::atomic<bool> _stop;
        std::condition_variable _cond;
        std::mutex _mutex;

        void check(const heartbeat_params params);
};

class Beacon { 
    public:
        Beacon(const heartbeat_params params);
        void clear();

    private:
        std::atomic<bool> _stop;
        std::condition_variable _cond;
        std::mutex _mutex;

        void ping(const heartbeat_params& params);
};

#endif
