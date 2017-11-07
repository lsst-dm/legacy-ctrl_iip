#include <iostream> 
#include <semaphore.h> 
#include <pthread.h> 
#include <signal.h>
#include "unistd.h"
#include <map> 

using namespace std; 

template <typename T> 
using funcptr = void (*T::*)(void *); 

class ThreadManager { 
    public: 
        template<typename T> 
        struct my_sem { 
            pthread_t thread; 
            sem_t sem_lock;
            funcptr<T> func_ptr;  
        }; 

        template<typename T> 
        ThreadManager(int num_threads, map<string, my_sem<T>*>); 
        ~ThreadManager(); 

        template<typename T> 
        void create_threads(int num_threads, map<string, my_sem<T>*>); 
        void start(int num_threads, sem_t threads_arr[]); 
}; 

class g { 
    public: 
        static void *hello(void *); 
        static void *bye(void *); 
}; 

template<typename T> 
ThreadManager::m(int num_threads, map<string, my_sem<T>*> threads_dict) { 
    create_threads(num_threads, threads_dict); 
} 

ThreadManager::~ThreadManager() {}

template<typename T>
void ThreadManager::create_threads(int num_threads, map<string, my_sem<T>*> threads_dict) { 
    sem_t threads_arr[num_threads]; 

    typename map<string, my_sem<T>*>::iterator it; 
    int count = 0; 
    for (it = threads_dict.begin(); it != threads_dict.end(); it++) { 
        string key = it->first; 
        struct my_sem<T> *sem_struct = it->second; 

        sem_init(&sem_struct->sem_lock, 0, 0); 
        pthread_create(&sem_struct->thread, NULL, g::hello, sem_struct); 
        threads_arr[count] = sem_struct->sem_lock; 
    } 
    
    start(num_threads, threads_arr); 
} 

void *g::hello(void *arg) { 
    /** 
    // my_sem* a = (my_sem*)arg; 

    while(1) { 
        sleep(1); 
        sem_post(&a->sem_lock); 
        cout << "HELLO" << endl; 
    } 
    */
} 

void *g::bye(void *arg) { 
    /**
    my_sem* a = (my_sem*)arg; 

    while(1) { 
        sleep(1); 
        sem_post(&a->sem_lock); 
        break;
    } 
    */ 
} 

void m::start(int num_threads, sem_t threads_arr[]) { 
    struct timespec time;
    time.tv_sec = 1000; 
    while(1) { 
        sleep(5); 
        for (int i = 0; i < num_threads; i++) { 
            sem_t s = threads_arr[i]; 
            int val = sem_timedwait(&s, &time); 
            cout << "VAL: " << val << endl; 
        } 
        //int val = sem_timedwait(&s1->sem_lock, &time); 
    } 
} 

int main() { 

    pthread_t t1, t2;
    sem_t s1, s2;

    struct ThreadManager::my_sem<g>* m1 = new m::my_sem<g>; 
    m1->thread = t1; 
    m1->sem_lock = s1; 
    m1->func_ptr = g::hello; 

    struct ThreadManager::my_sem<g>* m2 = new m::my_sem<g>; 
    m2->thread = t2; 
    m2->sem_lock = s2; 

    map<string, m::my_sem<g>*> mymap; 
    mymap["thread-1"] = m1;
    mymap["thread-2"] = m2;

    m m(2, mymap);     
    return 0; 
} 
