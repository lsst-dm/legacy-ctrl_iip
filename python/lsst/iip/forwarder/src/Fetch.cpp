#include <fstream>
#include <string>
#include <sstream>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>

#include "daq/Location.hh"
#include "daq/LocationSet.hh"
#include "ims/Store.hh"
#include "ims/Image.hh"
#include "ims/Source.hh"
#include "ims/Slice.hh"
#include "ims/Science.hh"

#include "../include/Fetch.h"
#include "../include/FileManifold.h"



Fetch::Fetch() {

  // Establish named pipe connections

  // Fork

  // Child process begins seeking for files to move from pipe data reads
  // Parent process continues init

Fetch::readout_image(readout_payload msg) {
  std::ofstream amp_segments[3][3][16];

  fm = FileManifold(amp_segments); 

  //setup_filehandles(amp_segments);

  //IMS::Store store(PARTITION);

  //IMS::Image image(IMAGE, store);

  //if DEBUG {image.synopsis();}

  //DAQ::LocationSet sources = image.sources();

  //DAQ::Location location;

  int board = 0;

  //while(sources.remove(location))
  //{
  //    reassemble_process(location, image, amp_segments, board);
  //    board++;
  //}

  fm.close_filehandles()
  //close_filehandles(amp_segments);

  return EXIT_SUCCESS;

//======================================================================

//Start in_visit_message consumer

//Start on_image_message consumer
////When take_image msg_type arrives, receive image sequence params
////Params will be:
//////Visit_Name or ImageSequence_Name
//////Science, and/or WFS,aand/or guide slices
//////Raft, and/or/maybe board, and/or/maybe CCD, /and/or/maybe segment.
//////Cross talk key if cross talk correction is to be used.
//////The destination where the file is going.
////These values will be stored in the Fetch component and will remain in use until a new take_image msg arrives

////When an end_readout msg_type arrives, the name of the image is queued in a fetch work queue.
////It is now up to the Fetch component to pull the named image from the DAQ using the specifications listed in 
////the take_image msg.

//Image fetch process:
////a thread runs that just fetches images according to name on image work queue
////After an image has been transferred, the image name is removed from the queue.

//For each image to be fetched:
////1) A directory is created using the DIR_PREFIX + the Visit_Name
////2) A FileManifold is created according to the directory name above and the take_image params
////   The FileManifold is a 3-dimensional array of file handles, or ofstream objects.
////3) The LocationSet calls are made and the sources are passed one at a time into a reassembly method with
////   the FileManifold where the individual slices of amp segment data are reassembled and written 
////   to the correct file handle(ofstream).
////4) The FileManifold.close() method is called
////5) A message is sent to the appropriate foreman stating that the readout and reassembly is complete.



}








