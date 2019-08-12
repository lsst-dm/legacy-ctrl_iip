#ifndef FILESENDER_H
#define FILESENDER_H

#include <boost/filesystem.hpp>

class FileSender {
    public:
        void send(const boost::filesystem::path&, const boost::filesystem::path&);
};

#endif
