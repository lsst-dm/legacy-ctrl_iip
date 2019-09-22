#include <iostream>
#include "forwarder/Formatter.h"
#include <vector>
#include <boost/filesystem.hpp>

using namespace std;
using namespace boost::filesystem;

int main() { 
    YAMLFormatter _fmt;
    vector<string> v {"01"}; 
    vector<string> pattern {
        "00", "01", "02", "03", "04", "05", "06", "07",
        "10", "11", "12", "13", "14", "15", "16", "17" 
    };
    _fmt.write_header("01", v, pattern, path("../tests/data/AT_pixel.fits"),
            path("../tests/data/AT_header.yml"));
}
