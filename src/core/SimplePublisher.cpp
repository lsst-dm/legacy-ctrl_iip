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
#include "core/SimplePublisher.h"
#include "core/SimpleLogger.h"
#include "core/Exceptions.h"

/** 
 * Rabbitmq Publisher that takes amqpurl to set up publishing messages
 *
 * @param url RabbitMQ url in the form of "amqp://username:passwd@100.100.0.0/%2fvhost"
 */ 
SimplePublisher::SimplePublisher(std::string url) { 
    try { 
        _channel = AmqpClient::Channel::CreateFromUri(url); 
    }
    catch (std::exception& e) { 
        throw L1::PublisherError(e.what());
    }
}

/** 
 * Publish message to the rabbitmq broker  
 * msg must be in the form of "{ MSG_TYPE: HELLO_WORLD }", which looks like python dictionary  
 *
 * @param queue_name rabbitmq queue to which the messages are being sent
 * @param msg message dictionary to publish to the queue
 */
void SimplePublisher::publish_message(std::string queue_name, std::string msg) {
    if (_channel) { 
        AmqpClient::BasicMessage::ptr_t message = AmqpClient::BasicMessage::Create(msg); 
        _channel->BasicPublish("", queue_name, message); 
    } 
}
