#include <yaml-cpp/yaml.h>
#include <iostream>

YAML::Node loadConfigFile(std::string filename);
std::string get_current_time(); 
int get_time_delta(std::string); 
