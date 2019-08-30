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

#include <exception>
#include "core/SimplePublisher.h"
#include "core/Exceptions.h"
#include "core/SimpleLogger.h"

SimplePublisher::SimplePublisher(const std::string& url) 
    try : RabbitConnection(url) { 
}
catch (L1::RabbitConnectionError& e) { 
    throw L1::PublisherError(e.what());
}

SimplePublisher::~SimplePublisher() { 
}

void SimplePublisher::publish_message(const std::string& queue, const std::string& body) {
    AmqpClient::BasicMessage::ptr_t message = AmqpClient::BasicMessage::Create(body); 
    try { 
        _channel->BasicPublish("", queue, message); 
    }
    catch (std::exception& e) { 
        std::string err = "Cannot publish " + body + " because " + e.what();
        LOG_CRT << err;
        throw L1::PublisherError(err);
    }
}
