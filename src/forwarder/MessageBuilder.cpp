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

#include <yaml-cpp/yaml.h>
#include "forwarder/MessageBuilder.h"

const std::string MessageBuilder::build_ack(const std::string& msg_type, 
                                            const std::string& component, 
                                            const std::string& ack_id, 
                                            const std::string& ack_bool) { 
    YAML::Emitter msg; 
    msg << YAML::DoubleQuoted;
    msg << YAML::Flow;
    msg << YAML::BeginMap; 
    msg << YAML::Key << "MSG_TYPE" << YAML::Value << msg_type + "_ACK"; 
    msg << YAML::Key << "COMPONENT" << YAML::Value << component; 
    msg << YAML::Key << "ACK_ID" << YAML::Value << ack_id; 
    // msg << YAML::Key << "ACK_BOOL" << YAML::Value << ack_bool; 
    msg << YAML::EndMap; 
    return std::string(msg.c_str());
}
