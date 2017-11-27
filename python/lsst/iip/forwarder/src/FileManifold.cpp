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



// Fetch entire designated raft
FileManiFold::FileManifold(const char* dir_prefix, const char* visit_name, const char* image_name, const char* raft) {


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
          fns << dir_prefix << visit_name \
                            << "/" \
                            << image_name \
                            << "--" << raft \
                            << "-ccd." << ccd_name \ 
                            << "_segment." << c;

          AMP_SEGMENTS[a][b][c].open(fns.str().c_str(), \
                                     std::ios::out | std::ios::app | std::ios::binary );
        }
      }
    }
  } // End FileManifold constructor for rafts



// Fetch only the designated CCD from the designated source board on the designated raft
FileManifold::FileManifold(const char* dir_prefix, 
               const char* visit_name, 
               const char* image_name, 
               const char* raft, 
               const char* ccd) {


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
    std::ostringstream fns;
    fns << dir_prefix << visit_name \
                      << "/" \
                      << image_name \
                      << "--" << raft \
                      << "-ccd." << ccd \ 
                      << "_segment." << c;

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
