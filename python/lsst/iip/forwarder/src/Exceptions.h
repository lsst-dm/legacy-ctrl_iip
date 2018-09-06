#include <string> 
#include <exception>
using namespace std;

class L1Exception: public exception { 
    private:
        string errormsg; 

    public: 
        L1Exception(const string& msg){
            errormsg = msg; 
        } 

        // virtual const char* what() const throw() { 
        virtual const char* what() const throw() { 
            return errormsg.c_str(); 
        } 
}; 

class L1Error : public L1Exception { 
    // Raise as general exception for main execution layer 
    public: 
        L1Error(const string& msg) : L1Exception(msg) {}
}; 

class L1YamlKeyError : public L1Exception { 
    // Raise when unable to process YAML messages 
    public: 
        L1YamlKeyError(const string& msg) : L1Exception(msg) {}
}; 

class L1RabbitConnectionError : public L1Exception { 
    // Raise when unable to connect to rabbit 
    public: 
        L1RabbitConnectionError(const string& msg) : L1Exception(msg) {}
}; 

class L1ConsumerError : public L1Error { 
    // Raise as general error for rabbit consumer 
    public: 
        L1ConsumerError(const string& msg) : L1Error(msg) {}
}; 

class L1PublisherError : public L1Error { 
    // Raise as general error for rabbit publisher
    public: 
        L1PublisherError(const string& msg) : L1Error(msg) {}
}; 

class L1ForwarderError : public L1Error { 
    // Raise as general error for forwarder
    public: 
        L1ForwarderError(const string& msg) : L1Error(msg) {}
}; 

class L1ConfigIOError : public L1Error { 
    // Raise when L1Config file cannot be opened 
    public: 
        L1ConfigIOError(const string& msg) : L1Error(msg) {}
}; 

class L1CannotCreateDirError: public L1Exception { 
    public: 
        L1CannotCreateDirError(const string& msg) : L1Exception (msg) {} 
}; 

class L1CannotCopyFileError: public L1Exception { 
    public: 
        L1CannotCopyFileError(const string& msg) : L1Exception(msg) {} 
}; 

class L1FitsFileError: public L1Exception { 
    // Raise when ciftiso api calls return error codes
    public: 
        L1FitsFileError(const string& msg) : L1Exception(msg) {}
};
