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
#include <stdio.h>
#include "SimplePublisher.h"

using namespace std; 
using namespace AmqpClient; 

SimplePublisher::SimplePublisher(string amqpurl) { 
    url = amqpurl;
    isConnected = connect(); 
}

bool SimplePublisher::connect() { 
    bool connection; 
    try { 
        channel = Channel::CreateFromUri(url); 
        connection = true; 
    } 
    catch (exception& e) { 
        connection = false; 
        cout << "Connection was not succesful." << endl; 
        cout << "SimplePublisher is quitting ... " << endl; 
        exit(100); 
    } 
    return connection;
}

void SimplePublisher::publish_message(string queue_name, string msg) {
    if (isConnected) { 
        BasicMessage::ptr_t message = BasicMessage::Create(msg); 
        channel->BasicPublish("", queue_name, message); 
    } 
}
