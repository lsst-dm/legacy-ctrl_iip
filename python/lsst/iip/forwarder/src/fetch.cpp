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

static const char STRIPE_ERROR[] = "%lli stripes reported, %i stripes expected\n";
static const char PIXEL_ERROR[] = "%lli pixels out of %lli pixels had errors\n";

#define EXPECTED_STRIPES 1111000 // Number of stripes in test image
#define PIX_MASK 0x3FFFF         // 18-bit Pixel Data Mask
#define N_AMPS 16                // Number of Amplifiers per CCD per Stripe

#define PARTITION argv[1]
#define IMAGE     argv[2]

static const char ERROR[] = "A partition and image name must be provided as a command line argument\n";

static void reassemble_process(const DAQ::Location&, const IMS::Image&, std::ofstream amp_segments[][3][16], int);
void setup_filehandles(std::ofstream amp_segments[][3][16]);
static void close_filehandles(std::ofstream amp_segments[][3][16]);

int main(int argc, char** argv)
{
  std::ofstream amp_segments[3][3][16];

  setup_filehandles(amp_segments); 

  IMS::Store store(PARTITION);

  IMS::Image image(IMAGE, store);

  image.synopsis();

  DAQ::LocationSet sources = image.sources();

  DAQ::Location location;

  int board = 0;

  while(sources.remove(location)) 
  {
      reassemble_process(location, image, amp_segments, board);
      board++; 
  }

  close_filehandles(amp_segments);

  return EXIT_SUCCESS;

}

void setup_filehandles(std::ofstream amp_segments[][3][16])
{
  //std::ofstream amp_segments[3][3][16]; // 3 Raft Elec. Boards, each with three CCDs, with 16 amps each

 for (int a=0; a<3; a++) // REBs
 {
   for (int b = 0; b < 3; b++) // CCDs
   {
     for (int c = 0; c < 16; c++) // Segments
      {
       std::ostringstream fns;
       fns << "/tmp/gunk/image_name-" << "REB." << a << "_ccd." << b << "_segment." << c;
       amp_segments[a][b][c].open(fns.str().c_str(), std::ios::out | std::ios::app | std::ios::binary );
      }
    }
 }

}

void close_filehandles(std::ofstream amp_segments[][3][16])
{

 for (int a=0; a<3; a++) // REBs
 {
   for (int b = 0; b < 3; b++) // CCDs
   {
     for (int c = 0; c < 16; c++) // Segments
      {
       amp_segments[a][b][c].close();
      }
    }
 }

}

void reassemble_process(const DAQ::Location& location, const IMS::Image& image, std::ofstream amp_segments[][3][16], int board)
{
  IMS::Source source(location, image);

  IMS::Science slice(source);

  if(!slice) return;

  uint64_t pixel = 0;
  uint64_t total_stripes = 0;
  uint64_t pixel_errors = 0;
  do
  {
    total_stripes += slice.stripes();
    IMS::Stripe* ccd0 = new IMS::Stripe [slice.stripes()];
    IMS::Stripe* ccd1 = new IMS::Stripe [slice.stripes()];
    IMS::Stripe* ccd2 = new IMS::Stripe [slice.stripes()];

    slice.decode012(ccd0, ccd1, ccd2);

    for(int s=0; s<slice.stripes(); ++s)
    {
      for(int amp=0; amp<N_AMPS; ++amp)
      { 
        if((++pixel&PIX_MASK) ^ ccd0[s].segment[amp]) ++pixel_errors;
        amp_segments[board][0][amp].write(reinterpret_cast<const char *>(&ccd0[s].segment[amp]), 1);
      }

      for(int amp=0; amp<N_AMPS; ++amp)
      {  
        if((++pixel&PIX_MASK) ^ ccd1[s].segment[amp]) ++pixel_errors;
        amp_segments[board][1][amp].write(reinterpret_cast<const char *>(&ccd1[s].segment[amp]), 1);
      }

      for(int amp=0; amp<N_AMPS; ++amp)
      {
        if((++pixel&PIX_MASK) ^ ccd2[s].segment[amp]) ++pixel_errors;
        amp_segments[board][2][amp].write(reinterpret_cast<const char *>(&ccd2[s].segment[amp]), 1);
      }

    }

    delete [] ccd0;
    delete [] ccd1;
    delete [] ccd2;

  }
  while(slice.advance());

  printf(STRIPE_ERROR, (long long int)total_stripes, EXPECTED_STRIPES);
  printf(PIXEL_ERROR, (long long int)pixel_errors, (long long int)pixel);

  return;

}
