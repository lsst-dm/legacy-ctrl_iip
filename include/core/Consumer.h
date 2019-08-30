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

#ifndef CONSUMER_H
#define CONSUMER_H

#include <iostream>
#include "core/RabbitConnection.h"

/**
 * Message Consumer interface to RabbitMQ Server
 *
 * Consumer is amqp message publishing object to RabbitMQ Server. It
 * extends connection to RabbitMQ server from RabbitConnection object.
 */
class Consumer : public RabbitConnection { 
    public:
        /**
         * Creates connection to RabbitMQ Server
         *
         * @param url AMQP Url to RabbbitMQ Server
         *      Example. `amqp://{user}:{password}@{hostname}/{vhost}`
         * @param queue Name of the queue to connect to
         *
         * @throws L1::ConsumerError Thrown if Consumer cannot connect
         *      to RabbitMQ Server
         * 
         * @exceptsafe Strong exception guarantee
         */
        Consumer(const std::string& url, const std::string& queue); 

        /**
         * Destruct Consumer
         */
        ~Consumer();

        /**
         * Start IO Loop to listen to messages
         *
         * @param on_message Function pointer to handle messages
         *
         * @throws L1::ConsumerError Thrown if Consumer cannot consume 
         *      messages from RabbitMQ Server
         */
        void run(std::function<void (const std::string&)> on_message);

    private:
        // RabbitMQ consume queue name
        std::string _queue; 
}; 

#endif
