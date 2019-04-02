/*
 * This file is part of ctrl_iip
 *
 * Developed for the LSST Data Management System.
 * This product includes software developed by the LSST Project
 * (https://www.lsst.org).
 * See the COPYRIGHT file at the top-level directory of this distribution
 * for details of code ownership.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include <cstdlib>
#include <ctime> 
#include <string>
#include <iostream> 
#include <yaml-cpp/yaml.h>

using namespace std; 

YAML::Node loadConfigFile(string filename) { 
    string config_filename;
    if (filename.empty()) { 
        config_filename = "L1SystemCfg.yaml"; 
    }
    else { 
        config_filename = filename;
    }

    const char* iip_config_dir = getenv("IIP_CONFIG_DIR");
    const char* ctrl_iip_dir = getenv("CTRL_IIP_DIR");
    if (iip_config_dir == NULL && ctrl_iip_dir == NULL) { 
        cout << "Please set environment variable CTRL_IIP_DIR or IIP_CONFIG_DIR" << endl;
        exit(-1);
    }

    string config_file;
    if (iip_config_dir == NULL) { 
        string config_dir(ctrl_iip_dir); 
        config_file = config_dir + "/etc/config/" + config_filename;
    }
    else { 
        string config_dir(iip_config_dir); 
        config_file = config_dir + "/" + config_filename;
    }
    
    try { 
	return YAML::LoadFile(config_file);
    }
    catch (YAML::BadFile& e) { 
	cout << "ERROR: L1SystemCfg file not found." << endl; 
	exit(EXIT_FAILURE); 
    } 
}

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
