/**
 * TODO: throw exceptions
 * TODO: add const
 * TODO: get_register_meta is wrong for science slice
 *
 * Exceptions:
 * * I can have bad axes number and stripe array allocation could fail
 */
#include <iostream>

#include "daq/Location.hh"
#include "ims/Image.hh"
#include "ims/Slice.hh"

#include "core/Exceptions.h"
#include "core/SimpleLogger.h"
#include "forwarder/DAQFetcher.h"

#define NUM_AMP 16
#define STRAIGHT_PIX_MASK 0x20000
#define WFS_PIX_MASK 0x20000
#define SCIENCE_PIX_MASK 0x1FFFF
#define PIX_MASK 0x3FFFF

using namespace std;
using namespace DAQ;
using namespace IMS;
using namespace RMS;
using namespace std::placeholders;
using namespace boost::filesystem;
using namespace L1;

using decode_science_func = void (Science&, int32_t**, const char&, const int32_t&);
using decode_wavefront_func = void (WaveFront&, int32_t**, const char&, const int32_t&);

DAQFetcher::DAQFetcher(const char* partition, string prefix) 
    : _store(partition), _prefix(prefix), _formatter() { 
}

void DAQFetcher::fetch(string image_id, string raft, string ccd, string board_type, const path& filepath) { 
    if (board_type == "Science") { 
        auto decoder = bind(&DAQFetcher::decode_science, this, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
        fetch_ccd<Science, decode_science_func>(image_id, raft, ccd, filepath, decoder);
    }
    else if (board_type == "WaveFront") { 
        auto decoder = bind(&DAQFetcher::decode_wavefront, this, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
        fetch_ccd<WaveFront, decode_wavefront_func>(image_id, raft, ccd, filepath, decoder);
    }
    else { 
        throw CannotFetchPixel("Board type is not in Science or WaveFront.");
    }
}

template<typename T, typename U>
int32_t* DAQFetcher::fetch_ccd(string image_id, string raft, string ccd, const path& filepath, function<U> decode) { 
    if (!has_image(image_id)) { 
        throw CannotFetchPixel("Image " + image_id + " does not exist in the catalog.");
    }
    Image image(image_id.c_str(), _store); 
    
    string bay_board = raft + "/" + ccd[0];
    Location location(bay_board.c_str());
    Source source(location, image);
    T slice(source);

    long naxes[2];
    get_naxes(source, naxes);

    long len = naxes[0] * naxes[1]; 

    PixelArray pixel_arr(NUM_AMP, len);
    int32_t** stripes = pixel_arr.get();

    int32_t total = 0; 
    bool canAdvance = true; 

    while (canAdvance) { 
        decode(slice, stripes, ccd[1], total);
        total += slice.stripes();
        canAdvance = slice.advance();  
    }

    _formatter.write_pix_file(stripes, total, naxes, filepath);
}

void DAQFetcher::decode_science(Science& slice, int32_t** pixel_data, const char& ccd, const int32_t& total) { 
    StripeArray stripe_array1(slice.stripes());
    Stripe* stripe1 = stripe_array1.get();

    StripeArray stripe_array2(slice.stripes());
    Stripe* stripe2 = stripe_array2.get();

    StripeArray stripe_array3(slice.stripes());
    Stripe* stripe3 = stripe_array3.get();

    slice.decode012(stripe1, stripe2, stripe3);
}

void DAQFetcher::decode_wavefront(WaveFront& slice, int32_t** pixel_data, const char& ccd,const int32_t& total) { 
    StripeArray stripe_array(slice.stripes());
    Stripe* stripe = stripe_array.get();
    slice.decode(stripe);

    for (int i = 0; i < NUM_AMP; i++) { 
        for (int j = 0; j < slice.stripes(); j++) { 
            pixel_data[i][total + j] = STRAIGHT_PIX_MASK ^ stripe[j].segment[i];
        }
    }
}

void DAQFetcher::get_naxes(const Source& source, long* naxes) { 
    const InstructionList* reglist = source.registers();
    const Instruction* inst0 = reglist->lookup(0);
    const Instruction* inst7 = reglist->lookup(7);
    const Instruction* inst1 = reglist->lookup(1);
    const Instruction* inst6 = reglist->lookup(6);
    const Instruction* inst8 = reglist->lookup(8);

    uint32_t operand0 = inst0->operand();
    uint32_t operand7 = inst7->operand();

    uint32_t operand1 = inst1->operand();
    uint32_t operand6 = inst6->operand();
    uint32_t operand8 = inst8->operand();

    long naxis_2 = operand0 + operand7;
    long naxis_1 = operand1 + operand6 + operand8;

    naxes[0] = naxis_1; 
    naxes[1] = naxis_2; 
}

bool DAQFetcher::has_image(const string& image_id) { 
    Images images(_store);
    const char* id = images.id();
    while (id) { 
        Image image(id, images);
        if (image_id == string(image.name())) { 
            return true;
        }
        id = images.id();
    }
    return false;
}

DAQFetcher::~DAQFetcher() {
}
