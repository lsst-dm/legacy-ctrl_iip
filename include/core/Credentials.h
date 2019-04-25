#include <iostream>
#include <yaml-cpp/yaml.h>

class Credentials {
    public: 
        YAML::Node credentials;

        Credentials(std::string);
        YAML::Node load_secure_file(std::string filename);
        std::string get_user(std::string);
        std::string get_passwd(std::string);
};
