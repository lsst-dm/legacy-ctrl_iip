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

#ifndef SIMPLE_PUBLISHER_H
#define SIMPLE_PUBLISHER_H

#include <iostream>
#include "core/RabbitConnection.h"

/**
 * Message Publisher interface to RabbitMQ Server
 *
 * SimplePublisher is amqp message publishing object to RabbitMQ Server. It
 * extends connection to RabbitMQ server from RabbitConnection object.
 */
class SimplePublisher : public RabbitConnection { 
    public: 
        /**
         * Creates connection to RabbitMQ Server
         *
         * @param url AMQP Url to RabbbitMQ Server
         *      Example. `amqp://{user}:{password}@{hostname}/{vhost}`
         *
         * @throws L1::PublisherError Thrown if SimplePublisher cannot connect
         *      to RabbitMQ Server
         * 
         * @exceptsafe Strong exception guarantee
         */
        SimplePublisher(const std::string& url); 

        /**
         * Destruct SimplePublisher
         */
        ~SimplePublisher();

        /**
         * Publish messages to RabbitMQ
         *
         * @param queue RabbitMQ queue to talk to
         * @param body Message body
         * 
         * @throws L1::PublisherError Thrown if it cannot publish message to 
         *      queue
         *
         * @exceptsafe Strong exception guarantee
         */
        void publish_message(const std::string& queue, const std::string& body); 
};

#endif
