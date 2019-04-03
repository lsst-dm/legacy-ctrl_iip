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

#include <cstdlib>
#include <pthread.h>
#include <stdio.h> 
#include <string.h>
#include <iostream>
#include <yaml-cpp/yaml.h>
#include "OCS_Bridge.h"
#include "Toolsmod.h"

using namespace std; 
using namespace YAML;

OCS_Bridge::OCS_Bridge() { 
    Node config_file = loadConfigFile("L1SystemCfg.yaml");
    Node root; 
    string base_name, base_passwd, base_addr; 
    try {  
	root = config_file["ROOT"]; 
	base_name = root["OCS"]["OCS_NAME"].as<string>(); 
	base_passwd = root["OCS"]["OCS_PASSWD"].as<string>(); 
	base_addr = root["BASE_BROKER_ADDR"].as<string>(); 
    } 
    catch (YAML::TypedBadConversion<string>& e) { 
	cout << "ERROR: In L1SystemCfg, cannot read ocs username, password or broker address from file." << endl; 
	exit(EXIT_FAILURE); 
    } 
    
    ostringstream broker_url;
    broker_url << "amqp://" << base_name << ":" << base_passwd << "@" << base_addr; 

    base_broker_addr = broker_url.str(); 

    cout << "AMQP: " << base_broker_addr << endl; 
    OCS_PUBLISH = root["OCS"]["OCS_PUBLISH"].as<string>(); 
    OCS_CONSUME = root["OCS"]["OCS_CONSUME"].as<string>(); 

    setup_publisher(); 
}

OCS_Bridge::~OCS_Bridge() {
    //delete ocs_publisher; 
} 

void OCS_Bridge::setup_publisher() { 
    cout << "Setting up RABBIT publisher" << endl; 
    ocs_publisher = new SimplePublisher(base_broker_addr); 
} 
