#include <pthread.h>
#include <stdio.h> 
#include <string.h>
#include <iostream>
#include <yaml-cpp/yaml.h>
#include "OCS_Bridge.h"

using namespace DDS;
using namespace dm;
using namespace std; 
using namespace YAML;

/* 
    OCS_Bridge handles configuration file opening and setting up publisher for rabbitmq
*/ 
OCS_Bridge::OCS_Bridge() { 
    Node config; 
    config = LoadFile("OCSDeviceCfg.yaml");

    Node root = config["ROOT"]; 
    string base_name = root["BASE_BROKER_NAME"].as<string>(); 
    string base_passwd = root["BASE_BROKER_PASSWD"].as<string>(); 
    string base_addr = root["BASE_BROKER_ADDR"].as<string>(); 
    
    ostringstream broker_url;
    broker_url << "amqp://" << base_name << ":" << base_passwd << "@" << base_addr; 

    base_broker_addr = broker_url.str(); 
    OCS_PUBLISH = root["OCS_PUBLISH"].as<string>(); 
    OCS_CONSUME = root["OCS_CONSUME"].as<string>(); 

    cout << "RUNNING THREADS >>>> " << endl; 

    setup_publisher(); 
}

/* destructor for OCS_Bridge */ 
OCS_Bridge::~OCS_Bridge() {
} 

/* 
    create rabbitmq publisher to send messages
*/ 
void OCS_Bridge::setup_publisher() { 
    cout << "Setting up RABBIT publisher" << endl; 
    SimplePublisher ocs_publisher(base_broker_addr); 
} 
