#include <semaphore.h> 
#include <iostream> 
#include <pthread.h>
#include <map> 

using funcptr = void * (*)(void *); 

class ThreadManager {
    public: 
        struct thread_arg { 
            pthread_t thread; 
            sem_t sem; 
            funcptr ptr; 
        };
        bool debug;         
        std::map<std::string, struct thread_arg*> threads_map; 
 
        ThreadManager(std::map<std::string, struct thread_arg*>); 
        ~ThreadManager(); 

        void create_threads();  
        void start(); 
        void create_a_thread(struct thread_arg*); 
}; 
