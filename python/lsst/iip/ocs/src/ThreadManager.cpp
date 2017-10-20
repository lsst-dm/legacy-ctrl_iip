#include <iostream> 
#include <pthread.h> 
#include <semaphore.h> 
#include <unistd.h> 
#include <map>
#include "Common.h"
#include "ThreadManager.h" 
#include "CommandListener.h"
#include "EventSubscriber.h"

using namespace std; 

ThreadManager::ThreadManager(int num_threads, map<string, Thread_t> *thread_dict) { 
    create_threads(&thread_dict); 
} 

void ThreadManager::create_threads(map<string, Thread_t> *thread_dict) { 
    for (auto& item : thread_dict) { 
        Thread_t *thread_args = item->second; 
    } 
} 

void ThreadManager::create_a_thread() { 

} 

void ThreadManager::run() {
    while (1) { 
        int wait_lock = sem_timedwait(&sem, 10); 
        if (wait_lock == -1) {  // 0 means success
            // restart thread
        } 
        usleep(5); 
    } 
} 

void ThreadManager::terminate() { 

} 

int main() { 
    pthread_t t1, t2; 
    sem_t s1, s2; 


    Thread_t m1; 
    m1.thread = t1; 
    m1.semaphore = s1; 
    m1.thread_name = "t-1"; 
    m1.funcptr = CommandListener::run_ar_start; 

    map<string, Thread_t> mymap; 
    mymap["t1"] = m1; 

    ThreadManager tman(1, mymap);
    return 0;
} 
