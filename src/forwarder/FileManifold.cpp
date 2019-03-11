/* FileManifold.cpp - www.lsst.org */

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
//Outer vector is for CCDs and inner is segments
vector<vector<std::ofstream>> raft_file_handles;

// Fetch entire designated raft
#FileManiFold::FileManifold(const char* dir_prefix, const char* visit_name, const char* image_name, const char* raft) {
FileManifold::FileManifold(const char* raft, 
               map<str, vector<string>> source_boards,
               const char image_id, 
               const char* dir_prefix) {

    char ccd[3][3] = { { "00","01","02"},
                       { "10","11","12"},
                       { "20","21","22"}  };


    // setup_filestreams 
    for (map<string,string>::iterator it = source_boards.begin(); it != source_boards.end(); ++it) { 
      string brd_tmpstr = it->first;
      vector<string> ccd_tmpvec = it.second;
      for (int i = 0; i < ccd_tmpvec.size(); i++) {  // CCDs 
        ccd_name = ccd_tmpvec[i];
        for (int j = 0; j < 16; j++) {   // Segments
          std::string seg; 
          if (c < 10) { 
              seg = "0" + to_string(c);
          } 
          else { 
              seg = to_string(c); 
          } 
          std::ostringstream fns;
          fns << dir_prefix << "/" \
                            << image_name \
                            << "--" << raft \
                            << "-ccd." << ccd_name \ 
                            << "_segment." << seg;

          AMP_SEGMENTS[a][b][c].open(fns.str().c_str(), \
                                     std::ios::out | std::ios::app | std::ios::binary );
        }
      }
    }
  } // End FileManifold constructor for rafts



// Fetch only the designated CCDs from the designated raft
FileManifold::FileManifold(const char* raft, 
               map<str, vector<string>> source_boards,
               const char image_id, 
               const char* dir_prefix) {


    // convert ccd into board so source is known
    int board = (-1)
    char ccds[3][3] = { { "00","01","02"},
                       { "10","11","12"},
                       { "20","21","22"}  };
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0;; j < 3; j++)
        {
            if (strcmp(ccd, ccds[i][j]) == 0)
            {
                board = i;
                break;
            }
        }
    }

  if (board == (-1)) /* something went wrong */
      return;

  for (int c = 0; c < 16; c++)  // Segments
  {
    std::string seg; 
    if (c < 10) { 
        seg = "0" + to_string(c);
    } 
    else { 
        seg = to_string(c); 
    } 
    std::ostringstream fns;
    fns << dir_prefix << visit_name \
                      << "/" \
                      << image_name \
                      << "--" << raft \
                      << "-ccd." << ccd \ 
                      << "_segment." << seg;

    CCD_SEGMENTS[c].open(fns.str().c_str(), \
                         std::ios::out | std::ios::app | std::ios::binary );
  }

    return;

} // End FileManifold constructor for one ccd
  


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
