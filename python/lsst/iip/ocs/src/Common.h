#include <pthread.h> 
#include <semaphore.h> 
#include <iostream> 

template <typename T> 
using funcptr = void (T::*)(void *); 
struct Thread_t { 
    pthread_t thread; 
    sem_t semaphore; 
    string thread_name; 
    funcptr run_func;  
}; 
