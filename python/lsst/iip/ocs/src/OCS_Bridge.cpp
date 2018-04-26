#include <pthread.h>
#include <stdio.h> 
#include <string.h>
#include <iostream>
#include <yaml-cpp/yaml.h>
#include "OCS_Bridge.h"

using namespace std; 
using namespace YAML;

OCS_Bridge::OCS_Bridge() { 
    Node config_file; 
    try { 
	config_file = LoadFile("./L1SystemCfg.yaml");
    }
    catch (YAML::BadFile& e) { 
	cout << "ERROR: L1SystemCfg file not found." << endl; 
	exit(EXIT_FAILURE); 
    } 

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
