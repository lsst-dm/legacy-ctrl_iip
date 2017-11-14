#include <fstream>
#include <string>
#include <sstream>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <yaml-cpp/yaml.h>

#include "FileManifold.h"


//  Names of CCDs and Boards ( Sources) in a raft
//    ________________
//    | 20 | 21 | 22 |  <---- Board 2
//    ----------------
//    | 10 | 11 | 12 |  <---- Board 1
//    ----------------
//    | 00 | 01 | 02 |  <---- Board 0
//    ----------------

using namespace YAML;


class FileManifold {

public:

  static const char* DIR_PREFIX;
  std::ofstream AMP_SEGMENTS[3][3][16];

  // Fetch entire designated raft
  FileManifold(const char* visit_name, const char* image_name, const char* raft) {

    //static const char* DIR_PREFIX = "/tmp/gunk/"
    DIR_PREFIX = get_directory_prefix()


    char ccd[3][3] = { { "00","01","02"},
                       { "10","11","12"},
                       { "20","21","22"}  };


    // setup_filestreams 
    for (int a = 0; a < 3; a++)  // REBs
    {  
      for (int b = 0; b < 3; b++) // CCDs 
      {
        ccd_name = ccd[a][b]
        for (int c = 0; c < 16; c++)  // Segments
        {
          std::ostringstream fns;
          fns << DIR_PREFIX << visit_name \
                            << "/" \
                            << image_name \
                            << "--" << raft \
                            << "-ccd." << ccd_name \ 
                            << "_segment." << c;

          amp_segments[a][b][c].open(fns.str().c_str(), \
                                     std::ios::out | std::ios::app | std::ios::binary );
        }
      }
    }
  } // End FileManifold constructor


  // Fetch only the designated CCD from the designated source board on the designated raft
FileManifold::FileManifold(const char* visit_name, 
               const char* image_name, 
               const char* raft, 
               const char* board, 
               const char* ccd) {
    return;
  }

char* FileManifold::get_directory_prefix(void)
{
    // Assign DIR_PREFIX to val in cfg file...
    char dir_prefix[40]; 
    Node config_file;
    try {
         config_file = LoadFile(CFG_FILE);
        }
    catch (YAML::BadFile& e) {
         cout << "ERROR: Config file not found." << endl;
         exit(EXIT_FAILURE);
        }

    Node root;
    try {
         root = config_file["ROOT"];
         dir_prefix = root["XFER_COMPONENTS"]["FWDR_DIR_PREFIX"].as<string>();
        }
    catch (YAML::TypedBadConversion<string>& e) {
        cout << "ERROR: In Config file, cant read FWDR_DIR_PREFIX." << endl;
        exit(EXIT_FAILURE);
       }

    return dir_prefix;


FileManifold::close_filehandles(void)
{
 for (int a=0; a<3; a++) // REBs
 {
  for (int b = 0; b < 3; b++) // CCDs
  {
   for (int c = 0; c < 16; c++) // Segments
   {
    AMP_SEGMENTS[a][b][c].close();
   }
  }
 }
} /* End close_filehandles */


} 
