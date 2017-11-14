#include <fstream>
#include <string>
#include <sstream>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "daq/Location.hh"
#include "daq/LocationSet.hh"
#include "ims/Store.hh"
#include "ims/Image.hh"
#include "ims/Source.hh"
#include "ims/Slice.hh"
#include "ims/Science.hh"

#include "FileManifold.h"


#define EXPECTED_STRIPES 1111000 // Number of stripes in test image
#define PIX_MASK 0x3FFFF         // 18-bit Pixel Data Mask
#define N_AMPS 16                // Number of Amplifiers per CCD per Stripe

#define PARTITION argv[1]
#define IMAGE     argv[2]

static const char ERROR[] = "A partition and image name are needed for command line argument\n";


class Fetch {
    public:

    /* Constructor */
    Fetch();

    /* Destructor */
    ~Fetch();

    /* create FileManifold object with proper file names */
     setup_filehandles(std::ofstream amp_segments[][3][16]);

    /* Reassemble slices and write to FileManifold */
    reassemble_process(const DAQ::Location&, const IMS::Image&, \
                       std::ofstream amp_segments[][3][16], int board_number);

    /* Child will remain in loop generally... */
    run_loop();

    /* Where the readout work is done */
    readout_payload readout_image(readout_payload msg);

    /* cleanup by closing all file handles (maybe not necessary with ofstreams) */
    close_filehandles(std::ofstream amp_segments[][3][16]);

    /* cleanupdirectory area */
    remove_files(char *visit_id);

};




