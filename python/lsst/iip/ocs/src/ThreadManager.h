#include <map> 
#include "Common.h"

class ThreadManager { 
    public: 
        
        ThreadManager(int, map<string, Thread_t>*); 
        ~ThreadManager(); 

        void create_threads(map<string, Thread_t>*); 
        void create_a_thread(); 
        void run(); 
        void terminate(); 
}; 
