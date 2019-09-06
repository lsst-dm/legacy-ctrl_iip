/* FileManifold.h */
#include <fstream>
#include <string>
#include <sstream>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <yaml-cpp/yaml.h>

//  Names of CCDs and Boards ( Sources) in a raft
//  //    ________________
//  //    | 20 | 21 | 22 |  <---- Board 2
//  //    ----------------
//  //    | 10 | 11 | 12 |  <---- Board 1
//  //    ----------------
//  //    | 00 | 01 | 02 |  <---- Board 0
//  //    ----------------
//

#define CFG_FILE "L1SystemCfg.yaml"
using namespace YAML;



class FileManifold {
    public:

    std::ofstream AMP_SEGMENTS[3][3][16];
    std::ofstream CCD_SEGMENTS[16];

    /* Beginning of directory path for files...read from config file */
    static const char* DIR_PREFIX;

    std::ofstream AMP_SEGMENTS[3][3][16];

    /* Constructor for typical raft fetch */
    FileManifold(const char* dir_prefix, const char* visit_name, const char* image_name, const char* raft);

    /* Constructor for single CCD fetch */
    FileManifold(const char* dir_prefix, 
                 const char* visit_name,
                 const char* image_name,
                 const char* raft,
                 const char* ccd); 

    /* Destructor calls close_filehandles and maybe rm's files */
    ~FileManifold();

    close_filehandles(void);


};





