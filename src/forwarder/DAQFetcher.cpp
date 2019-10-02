/*
 * This file is part of ctrl_iip
 *
 * Developed for the LSST Data Management System.
 * This product includes software developed by the LSST Project
 * (https://www.lsst.org).
 * See the COPYRIGHT file at the top-level directory of this distribution
 * for details of code ownership.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
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

namespace fs = boost::filesystem;

using decode_science_func = void (IMS::Science&, 
                                  int32_t**, 
                                  const char&, 
                                  const int32_t&);

using decode_wavefront_func = void (IMS::WaveFront&, 
                                    int32_t**, 
                                    const char&, 
                                    const int32_t&);

DAQFetcher::DAQFetcher(const char* partition) 
    : _store(partition), _formatter() { 
}

void DAQFetcher::fetch(const std::string& image_id, 
                       const std::string& raft, 
                       const std::string& ccd, 
                       const std::string& board_type, 
                       const fs::path& filepath) { 
    if (board_type == "Science") { 
        auto decoder = bind(&DAQFetcher::decode_science, 
                            this, 
                            std::placeholders::_1, 
                            std::placeholders::_2, 
                            std::placeholders::_3, 
                            std::placeholders::_4);
        fetch_ccd<IMS::Science, decode_science_func>(image_id, raft, ccd, filepath, decoder);
    }
    else if (board_type == "WaveFront") { 
        auto decoder = bind(&DAQFetcher::decode_wavefront, this, 
                std::placeholders::_1, std::placeholders::_2, std::placeholders::_3, std::placeholders::_4);
        fetch_ccd<IMS::WaveFront, decode_wavefront_func>(image_id, raft, ccd, filepath, decoder);
    }
    else { 
        std::string err = "Board type is not in Science or WaveFront.";
        LOG_CRT << err;
        throw L1::CannotFetchPixel(err);
    }
}

template<typename T, typename U>
int32_t* DAQFetcher::fetch_ccd(const std::string& image_id, 
                               const std::string& raft, 
                               const std::string& ccd, 
                               const fs::path& filepath, 
                               std::function<U> decode) { 
    try { 
        if (!has_image(image_id)) { 
            std::string err = "Image " + image_id + " does not exist in the catalog.";
            LOG_CRT << err;
            throw L1::CannotFetchPixel(err); 
        }
        IMS::Image image(image_id.c_str(), _store); 
        
        std::string bay_board = raft + "/" + ccd[0];

        // Should throw exception from DAQ api, instead of SIGABRT
        DAQ::Location location(bay_board.c_str());
        IMS::Source source(location, image);
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
    catch (L1::CannotFormatFitsfile& e) { 
        throw L1::CannotFetchPixel(e.what());
    }
}

void DAQFetcher::decode_science(IMS::Science& slice, 
                                int32_t** pixel_data, 
                                const char& ccd, 
                                const int32_t& total) { 
    StripeArray stripe_array1(slice.stripes());
    IMS::Stripe* stripe1 = stripe_array1.get();

    StripeArray stripe_array2(slice.stripes());
    IMS::Stripe* stripe2 = stripe_array2.get();

    StripeArray stripe_array3(slice.stripes());
    IMS::Stripe* stripe3 = stripe_array3.get();

    slice.decode012(stripe1, stripe2, stripe3);
}

void DAQFetcher::decode_wavefront(IMS::WaveFront& slice, 
                                  int32_t** pixel_data, 
                                  const char& ccd,
                                  const int32_t& total) { 
    StripeArray stripe_array(slice.stripes());
    IMS::Stripe* stripe = stripe_array.get();
    slice.decode(stripe);

    for (int i = 0; i < NUM_AMP; i++) { 
        for (int j = 0; j < slice.stripes(); j++) { 
            pixel_data[i][total + j] = STRAIGHT_PIX_MASK ^ stripe[j].segment[i];
        }
    }
}

void DAQFetcher::get_naxes(const IMS::Source& source, long* naxes) { 
    const RMS::InstructionList* reglist = source.registers();
    const RMS::Instruction* inst0 = reglist->lookup(0);
    const RMS::Instruction* inst7 = reglist->lookup(7);
    const RMS::Instruction* inst1 = reglist->lookup(1);
    const RMS::Instruction* inst6 = reglist->lookup(6);
    const RMS::Instruction* inst8 = reglist->lookup(8);

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

bool DAQFetcher::has_image(const std::string& image_id) { 
    IMS::Images images(_store);
    const char* id = images.id();
    while (id) { 
        IMS::Image image(id, images);
        if (image_id == std::string(image.name())) { 
            return true;
        }
        id = images.id();
    }
    return false;
}

DAQFetcher::~DAQFetcher() {
}
