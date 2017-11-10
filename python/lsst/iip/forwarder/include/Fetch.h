#define EXPECTED_STRIPES 1111000 // Number of stripes in test image
#define PIX_MASK 0x3FFFF         // 18-bit Pixel Data Mask
#define N_AMPS 16                // Number of Amplifiers per CCD per Stripe

#define PARTITION argv[1]
#define IMAGE     argv[2]

static const char ERROR[] = "A partition and image name are needed for command line argument\n";

static void reassemble_process(const DAQ::Location&, const IMS::Image&, std::ofstream amp_segments[][3][16], int);

void setup_filehandles(std::ofstream amp_segments[][3][16]);

static void close_filehandles(std::ofstream amp_segments[][3][16]);



