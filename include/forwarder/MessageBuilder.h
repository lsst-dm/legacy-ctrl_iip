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

#include <iostream>

class MessageBuilder { 
    public:
        const std::string build_ack(const std::string& msg_type, 
                                    const std::string& component, 
                                    const std::string& ack_id, 
                                    const std::string& ack_bool);
        const std::string build_xfer_complete(const std::string& filename,
                                              const std::string& session_id,
                                              const std::string& job_num,
                                              const std::string& reply_q);
        const std::string build_associated_ack(const std::string& key);
        const std::string build_fwd_info(const std::string& hostname,
                                         const std::string& ip_addr,
                                         const std::string& consume_q);
};
