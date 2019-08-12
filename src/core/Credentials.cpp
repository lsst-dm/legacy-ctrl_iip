#include <boost/filesystem.hpp>
#include "Credentials.h"
#include "SimpleLogger.h"

using namespace YAML;
using namespace std;
namespace fs = boost::filesystem;

Credentials::Credentials(string filename) { 
    this->credentials = load_secure_file(filename);
}

Node Credentials::load_secure_file(string filename) { 
    fs::path home = string(getenv("HOME"));
    fs::path lsst = ".lsst"; 
    fs::path dirpath = home / lsst;
    fs::path filepath = dirpath / filename;
    LOG_DBG << "Secure filepath is " << filepath;
    if (!fs::exists(filepath)) { 
        ostringstream message;
        message << "Secure file " << filename << " doesn't exist.";
        cout << message.str() << endl;
        LOG_CRT << message.str();
        exit(-1);
    }
    fs::perms dirperm = fs::status(dirpath).permissions();
    fs::perms fileperm = fs::status(filepath).permissions();
    if (dirperm != fs::owner_all) { 
        ostringstream message;
        message <<  "Directory " << dirpath << " is not secure.";
        cout << message.str() << endl;
        cout << "Please run `chmod 700 " << dirpath << "` to fix it." << endl;
        LOG_CRT << message.str();
        exit(-1);
    }
    if (fileperm != (fs::owner_read | fs::owner_write)) { 
        ostringstream message;
        message << "File " << filepath << " is not secure.";
        cout << message.str() << endl;
        cout << "Please run `chmod 600 " << filepath << "` to fix it." << endl;
        LOG_CRT << message.str();
        exit(-1);
    }
    try { 
        return LoadFile(filepath.string());
    }
    catch (BadFile& e) { 
        LOG_CRT << "Cannot read secure file " << filepath;
        exit(-1); 
    }  
}

string Credentials::get_user(string user_alias) { 
    try { 
        string user = this->credentials["rabbitmq_users"][user_alias].as<string>();
        return user;
    }
    catch (YAML::TypedBadConversion<string>& e) { 
	LOG_CRT  << "Cannot read rabbitmq username from secure file";
	exit(-1); 
    }
}

string Credentials::get_passwd(string passwd_alias) { 
    try { 
        string passwd = this->credentials["rabbitmq_users"][passwd_alias].as<string>();
        return passwd;
    }
    catch (YAML::TypedBadConversion<string>& e) { 
	LOG_CRT << "Cannot read rabbitmq password from secure file";
	exit(-1); 
    }
}
