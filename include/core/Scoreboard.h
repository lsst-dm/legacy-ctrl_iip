#ifndef SCOREBOARD_H
#define SCOREBOARD_H

#include <iostream>
#include <vector>
#include <map>

class Scoreboard {
    public:
        Scoreboard();
        ~Scoreboard();

        bool is_ready(const std::string&);
        void init(const std::string&);
        void add(const std::string&, const std::string&);
        void remove(const std::string&);

    private:
        std::map<std::string, std::vector<std::string> > _db;
};

#endif
