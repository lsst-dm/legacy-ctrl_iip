#ifndef EXCEPTIONS_H
#define EXCEPTIONS_H

#include <exception>

namespace L1 { 
    class L1Exception: public std::exception { 
        private:
            std::string errormsg; 

        public: 
            L1Exception(const std::string& msg){
                errormsg = msg; 
            } 

            virtual const char* what() const throw() { 
                return errormsg.c_str(); 
            } 
    }; 

    class YamlKeyError : public L1Exception { 
        // Raise when unable to process YAML messages 
        public: 
            YamlKeyError(const std::string& msg) : L1Exception(msg) {}
    }; 

    class RabbitConnectionException : public L1Exception { 
        // Raise when unable to connect to rabbit 
        public: 
            RabbitConnectionException(const std::string& msg) : L1Exception(msg) {}
    }; 

    class ConsumerException : public L1Exception { 
        // Raise as general error for rabbit consumer 
        public: 
            ConsumerException(const std::string& msg) : L1Exception(msg) {}
    }; 

    class PublisherError : public L1Exception { 
        // Raise as general error for rabbit publisher
        public: 
            PublisherError(const std::string& msg) : L1Exception(msg) {}
    }; 

    class ForwarderException : public L1Exception { 
        // Raise as general error for forwarder
        public: 
            ForwarderException(const std::string& msg) : L1Exception(msg) {}
    }; 

    class ConfigIOError : public L1Exception { 
        // Raise when L1Config file cannot be opened 
        public: 
            ConfigIOError(const std::string& msg) : L1Exception(msg) {}
    }; 

    class CannotCreateDir: public L1Exception { 
        public: 
            CannotCreateDir(const std::string& msg) : L1Exception (msg) {} 
    }; 

    class CannotCopyFile: public L1Exception { 
        public: 
            CannotCopyFile(const std::string& msg) : L1Exception(msg) {} 
    }; 

    class NoHeader: public L1Exception { 
        public: 
            NoHeader(const std::string& msg) : L1Exception(msg) {} 
    }; 

    class FileExists: public L1Exception { 
        public: 
            FileExists(const std::string& msg) : L1Exception(msg) {} 
    }; 

    class NoCURLHandle: public L1Exception { 
        public: 
            NoCURLHandle(const std::string& msg) : L1Exception(msg) {} 
    }; 

    class CfitsioError: public L1Exception { 
        public: 
            CfitsioError(const std::string& msg) : L1Exception(msg) {} 
    }; 

    class CannotFormatFitsfile: public L1Exception { 
        public: 
            CannotFormatFitsfile(const std::string& msg) : L1Exception(msg) {} 
    }; 

    class CannotFetchPixel: public L1Exception { 
        public: 
            CannotFetchPixel(const std::string& msg) : L1Exception(msg) {} 
    }; 
};

#endif
