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
#include <unistd.h>
#include <stdlib.h>
#include "core/Consumer.h"

using namespace std; 
using namespace AmqpClient;
  
Consumer::Consumer(string amqp_url, string queue) { 
    URL = amqp_url; 
    EXCHANGE = "message"; 
    QUEUE = queue; 
    SLEEPING_MS = 5000;
    isReconnected = false;
} 

void Consumer::connect() { 
    try { 
        channel = Channel::CreateFromUri(URL); 
        on_connection_open(); 
    } 
    catch (exception& e) { 
        if (!isReconnected)  { 
            cout << "EXCEPTION: " << e.what() << endl; 
            on_connection_closed(); 
        }
        else { exit(EXIT_FAILURE); }   
    } 
} 

void Consumer::on_connection_open() { 
    cout << "Connection was successful" << endl; 
    // setup_exchange(); 
} 

void Consumer::on_connection_closed() { 
    cout << "Connection was closed. " << endl; 
    usleep(SLEEPING_MS);     
    reconnect(); 
} 

void Consumer::reconnect() { 
    isReconnected = true; 
    connect(); 
} 

void Consumer::setup_exchange() { 
    cout << "Setting up exchange" << endl; 
    channel->DeclareExchange(EXCHANGE);
    on_exchange_declareok();
} 

void Consumer::on_exchange_declareok() { 
    cout << "Exchange set up was successful" << endl; 
    setup_queue(); 
} 

void Consumer::setup_queue() { 
    cout << "Setting up queue" << endl; 
    channel->DeclareQueue(QUEUE, false, false, false, false); 
    on_queue_declareok();
} 

void Consumer::on_queue_declareok() { 
    cout << "Queue declare was successful" << endl; 
    on_bind_declareok(); 
} 

void Consumer::on_bind_declareok() { 
    cout << "Binding queue with exchange" << endl; 
    channel->BindQueue(QUEUE, EXCHANGE, QUEUE); 
} 

void Consumer::run(function<void (const string&)> on_message) { 
    cout << "##### Start consuming messages ######" << endl;
    try {
        connect(); 
        string consume_tag = channel->BasicConsume(QUEUE); 
        while (1) {
            Envelope::ptr_t envelope = channel->BasicConsumeMessage(consume_tag); 
            BasicMessage::ptr_t messageEnv = envelope->Message(); 
            string message = messageEnv->Body();
            on_message(message);
        }
    }
    catch (exception& e) { 
        cout << e.what() << endl;
    }
} 
