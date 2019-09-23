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

#include <iostream> 
#include <exception> 
#include "core/Exceptions.h"
#include "core/SimpleLogger.h"
#include "core/Consumer.h"

const unsigned int sleeping_ms = 5000;
const std::string exchange = "message"; 
  
Consumer::Consumer(const std::string& url, const std::string& queue) 
    try : RabbitConnection(url), _queue(queue) { 
} 
catch (L1::RabbitConnectionError& e) { 
    throw L1::ConsumerError(e.what());
}

Consumer::~Consumer() { 
}

void Consumer::run(std::function<void (const std::string&)> on_message) { 
    try {
        std::string consume_tag = _channel->BasicConsume(_queue); 
        LOG_INF << "==== Started consuming messages from " << _queue;
        while (true) {
            AmqpClient::Envelope::ptr_t envelope = _channel->BasicConsumeMessage(consume_tag); 
            AmqpClient::BasicMessage::ptr_t messageEnv = envelope->Message(); 
            std::string message = messageEnv->Body();
            on_message(message);
        }
    }
    catch (std::exception& e) { 
        std::string err = "Cannot consume messages from " + _queue + " because " + e.what();
        LOG_CRT << err; 
        throw L1::ConsumerError(err);
    }
} 
