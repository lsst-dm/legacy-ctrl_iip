#include "core/Scoreboard.h"

using namespace std;

int NUM_EVENTS = 2;

Scoreboard::Scoreboard() { 

}

Scoreboard::~Scoreboard() { 

}

bool Scoreboard::is_ready(const string& image_id) { 
    auto list = _db[image_id];
    if (list.size() == NUM_EVENTS) { 
        return true; 
    }
    return false;
} 

void Scoreboard::init(const string& image_id) { 
    vector<string> events;
    _db[image_id] = events;
}

void Scoreboard::add(const string& image_id, const string& event) { 
    auto list = _db[image_id];
    list.push_back(event);
    _db[image_id] = list;
}

void Scoreboard::remove(const string& image_id) {
    _db.erase(image_id);
}
