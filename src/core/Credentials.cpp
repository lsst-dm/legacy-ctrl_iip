#include <boost/filesystem.hpp>
#include "Credentials.h"
#include "SimpleLogger.h"
BOOST_LOG_INLINE_GLOBAL_LOGGER_DEFAULT(lg, src::severity_logger_mt< severity_level >);
#include "IIPMacro.h"

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
        LOG_CRT << "Secure file " << filename << " doesn't exist.";
        exit(-1);
    }
    fs::perms dirperm = fs::status(dirpath).permissions();
    fs::perms fileperm = fs::status(filepath).permissions();
    if (dirperm != fs::owner_all) { 
        ostringstream message;
        message <<  "Directory " << dirpath << " is not secure.";
        LOG_CRT << message;
        cout << message << endl;
        cout << "Please run `chmod 700 " << dirpath << "` to fix it." << endl;
        exit(-1);
    }
    if (fileperm != (fs::owner_read | fs::owner_write)) { 
        ostringstream message;
        message << "File " << filepath << " is not secure.";
        LOG_CRT << message;
        cout << message << endl;
        cout << "Please run `chmod 600 " << filepath << "` to fix it." << endl;
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
        LOG_DBG << "Secure rabbitmq username is " << user;
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
        LOG_DBG << "Secure rabbitmq passwd is " << passwd;
        return passwd;
    }
    catch (YAML::TypedBadConversion<string>& e) { 
	LOG_CRT << "Cannot read rabbitmq password from secure file";
	exit(-1); 
    }
}
