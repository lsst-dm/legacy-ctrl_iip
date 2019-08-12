#ifndef EXCEPTIONS_H
#define EXCEPTIONS_H

#include <string> 
#include <exception>
using namespace std;

namespace L1 { 
    class L1Exception: public exception { 
        private:
            string errormsg; 

        public: 
            L1Exception(const string& msg){
                errormsg = msg; 
            } 

            virtual const char* what() const throw() { 
                return errormsg.c_str(); 
            } 
    }; 

    class YamlKeyError : public L1Exception { 
        // Raise when unable to process YAML messages 
        public: 
            YamlKeyError(const string& msg) : L1Exception(msg) {}
    }; 

    class RabbitConnectionException : public L1Exception { 
        // Raise when unable to connect to rabbit 
        public: 
            RabbitConnectionException(const string& msg) : L1Exception(msg) {}
    }; 

    class ConsumerException : public L1Exception { 
        // Raise as general error for rabbit consumer 
        public: 
            ConsumerException(const string& msg) : L1Exception(msg) {}
    }; 

    class PublisherException : public L1Exception { 
        // Raise as general error for rabbit publisher
        public: 
            PublisherException(const string& msg) : L1Exception(msg) {}
    }; 

    class ForwarderException : public L1Exception { 
        // Raise as general error for forwarder
        public: 
            ForwarderException(const string& msg) : L1Exception(msg) {}
    }; 

    class ConfigIOError : public L1Exception { 
        // Raise when L1Config file cannot be opened 
        public: 
            ConfigIOError(const string& msg) : L1Exception(msg) {}
    }; 

    class CannotCreateDir: public L1Exception { 
        public: 
            CannotCreateDir(const string& msg) : L1Exception (msg) {} 
    }; 

    class CannotCopyFile: public L1Exception { 
        public: 
            CannotCopyFile(const string& msg) : L1Exception(msg) {} 
    }; 

    class NoHeader: public L1Exception { 
        public: 
            NoHeader(const string& msg) : L1Exception(msg) {} 
    }; 

    class FileExists: public L1Exception { 
        public: 
            FileExists(const string& msg) : L1Exception(msg) {} 
    }; 

    class NoCURLHandle: public L1Exception { 
        public: 
            NoCURLHandle(const string& msg) : L1Exception(msg) {} 
    }; 

    class CfitsioError: public L1Exception { 
        public: 
            CfitsioError(const string& msg) : L1Exception(msg) {} 
    }; 

    class CannotFormatFitsfile: public L1Exception { 
        public: 
            CannotFormatFitsfile(const string& msg) : L1Exception(msg) {} 
    }; 

    class CannotFetchPixel: public L1Exception { 
        public: 
            CannotFetchPixel(const string& msg) : L1Exception(msg) {} 
    }; 
};

#endif
