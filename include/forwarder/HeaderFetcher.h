#ifndef HEADERFETCHER_H
#define HEADERFETCHER_H

#include <boost/filesystem.hpp>
#include <curl/curl.h>
#include <stdio.h>

class HeaderFetcher { 
    public:
        HeaderFetcher();
        ~HeaderFetcher();
        void fetch(const std::string&, const boost::filesystem::path&);
  
    private:
        CURL* handle;
};

class FileOpener { 
    public:
        FileOpener(const boost::filesystem::path&);
        ~FileOpener();
        FILE* get();
        void set_remove();

    private:
        FILE* _file;
        bool _remove;
        boost::filesystem::path _filename;
};

class CURLHandle { 
    public:
        CURLHandle();
        ~CURLHandle();
        CURL* get();

    private:
        CURL* _handle;
};

#endif
