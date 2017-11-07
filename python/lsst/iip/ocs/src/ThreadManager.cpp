#include "unistd.h" 
#include "ThreadManager.h"

using namespace std; 

class G { 
    public: 
        static void *hello(void *); 
        static void *bye(void *); 
}; 

ThreadManager::ThreadManager(map<string, struct thread_arg*> threads_dict) { 
    this->threads_map = threads_dict;  
    this->debug = false; 
    create_threads();     
} 

ThreadManager::~ThreadManager() {}; 

void ThreadManager::create_threads() { 
    map<string, struct thread_arg*>::iterator it; 
    for (it = this->threads_map.begin(); it != this->threads_map.end(); it++){ 
        struct thread_arg* m = it->second;
        pthread_create(&m->thread, NULL, m->ptr, m); 
    } 
} 

void ThreadManager::create_a_thread(struct thread_arg* h) { 
    pthread_create(&h->thread, NULL, h->ptr, h); 
} 

void ThreadManager::start() { 
    struct timespec time; 
    time.tv_sec = 1000; 
    map<string, struct thread_arg*>::iterator it; 

    while(1) { 
        sleep(5); 
        for (it = this->threads_map.begin(); it != this->threads_map.end(); it++) { 
            struct thread_arg* m = it->second; 
            int val = sem_timedwait(&m->sem, &time); 
            if (debug && val == -1) { 
                create_a_thread(m); 
            } 
            cout << "Thread: " << it->first << endl; 
            cout << "VAL: " << val << endl; 
        }         
    } 
} 

void *G::hello(void *parg) { 
    struct ThreadManager::thread_arg* arg = (struct ThreadManager::thread_arg*)parg; 
    
    while(1) { 
        sleep(1); 
        //sem_post(&arg->sem); 
        cout << "HELLO" << endl; 
    }  
} 

void *G::bye(void *parg) { 
    struct ThreadManager::thread_arg* arg = (struct ThreadManager::thread_arg*)parg; 
    
    while(1) { 
        sleep(2); 
        sem_post(&arg->sem); 
        cout << "BYE" << endl; 
    }  
} 

int main() { 
    pthread_t t1, t2; 
    sem_t s1, s2; 
    sem_init(&s1, 0, 0); 
    sem_init(&s2, 0, 0); 

    struct ThreadManager::thread_arg* g1 = new ThreadManager::thread_arg; 
    g1->thread = t1; 
    g1->sem = s1; 
    g1->ptr = G::hello; 

    struct ThreadManager::thread_arg* g2 = new ThreadManager::thread_arg; 
    g2->thread = t1; 
    g2->sem = s1; 
    g2->ptr = G::bye;
  
    map<string, struct ThreadManager::thread_arg*> mymap; 
    mymap["thread-1"] = g1; 
    mymap["thread-2"] = g2;
    ThreadManager tm(mymap); 
    tm.start(); 
    return 0;
} 
