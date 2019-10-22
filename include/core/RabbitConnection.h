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

#ifndef RABBIT_CONNECTION_H
#define RABBIT_CONNECTION_H

#include <iostream>
#include <SimpleAmqpClient/SimpleAmqpClient.h>

/**
 * Create connection to RabbitMQ Server
 */
class RabbitConnection { 
    public:
        /**
         * Create connection to RabbitMQ Server
         *
         * @param url RabbitMQ URL of the form
         *      `amqp://{username}:{password}@{hostname}/{vhost}`
         *
         * @throws L1::RabbitConnectionError if application cannot make
         *      connection to RabbitMQ Server
         */
        RabbitConnection(const std::string& url);

        /**
         * Destructs RabbitConnection
         */
        ~RabbitConnection();

    protected:
        // Amqp Channl object used for connecting to RabbitMQ Server
        AmqpClient::Channel::ptr_t _channel;  
};

#endif
