#include <iostream>
#include <sstream>

#include "core/SimpleLogger.h"
#include "core/Exceptions.h"
#include "forwarder/FileSender.h"

using namespace std;
using namespace boost::filesystem;
using namespace L1;

void FileSender::send(const path& from, const path& to) { 
    const char* home = getenv("HOME"); 
    path private_key = path(home) / path(".ssh/id_rsa");
    if (!exists(private_key)) { 
        throw CannotCopyFile("Private key does not exist.");
    }

    // -f, forces the copy, if file exists, delete and copy
    // -n, does not use DNS to resolve IP addresses
    ostringstream bbcp;
    bbcp << "bbcp"
         << " -f "
         << " -n "
         << " -i " << private_key << " "
         << from.string()
         << " "
         << to.string();
    int status = system(bbcp.str().c_str());
    if (status) { 
        throw CannotCopyFile("Cannot copy file from " + from.string() + " to " + to.string());
    }

    LOG_INF << "Sent file from " + from.string() + " to " + to.string();
}
