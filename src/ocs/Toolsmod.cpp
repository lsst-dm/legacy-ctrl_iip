#include <ctime> 
#include <string>
#include <iostream> 

using namespace std; 

string get_current_time() { 
    time_t t = time(0); 
    struct tm* now = localtime(&t); 
    int year = now->tm_year + 1900; 
    int month = now->tm_mon + 1; 
    int day = now->tm_mday; 
    int hour = now->tm_hour; 
    int min = now->tm_min; 
    int sec = now->tm_sec; 

    string cur_time = to_string(year) + "-" + to_string(month) + "-" + to_string(day) + " " + to_string(hour)
		    + ":" + to_string(min) + ":" + to_string(sec) + ".\n"; 
    return cur_time;  
} 

int get_time_delta(string time_arg) { 
    time_t t = time(0); 
    struct tm* now = localtime(&t); 
    int year = now->tm_year + 1900; 
    int month = now->tm_mon + 1; 
    int day = now->tm_mday; 
    int hour = now->tm_hour; 
    int cur_min = now->tm_min; 
    int cur_sec = now->tm_sec; 

    // currently concerning min and sec, more robust should compare years ... 
    // assuming this is happening in same month and year
    string hour_min = time_arg.substr(time_arg.find(" "), 9); 
    string arg_min = hour_min.substr(4, 2); 
    string arg_sec = hour_min.substr(7, 2); 
    
    int cur_time = cur_min * 60 + cur_sec; 
    int arg_time = stoi(arg_min) * 60 + stoi(arg_sec); 
    int delta_time = cur_time - arg_time; 
    
    return delta_time; 
}
