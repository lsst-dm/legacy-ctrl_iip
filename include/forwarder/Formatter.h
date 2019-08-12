#ifndef FORMATTER_H
#define FORMATTER_H

#include <fitsio.h>
#include <boost/filesystem.hpp>

class Formatter { 
    public:
        void write_pix_file(int32_t**, int32_t&, long*, const boost::filesystem::path&);
};

class FitsFormatter : public Formatter { 
    public:
        void write_header(const boost::filesystem::path&, const boost::filesystem::path&);
        bool contains_excluded_key(char*);
};

class FitsOpener { 
    public:
        FitsOpener(const boost::filesystem::path&, int);
        ~FitsOpener();
        fitsfile* get();
        int num_hdus();
    private:
        fitsfile* _fptr;
        int _status; 
};

enum FILE_MODE { 
    WRITE_ONLY = -1
};

#endif
