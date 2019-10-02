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

#include <functional>
#include <boost/filesystem.hpp>

#include "ims/Store.hh"
#include "ims/Source.hh"
#include "ims/WaveFront.hh"
#include "ims/Science.hh"

#include "Formatter.h"

class DAQFetcher { 
    public:
        DAQFetcher(const char*);
        ~DAQFetcher();

        void fetch(const std::string&, 
                   const std::string&, 
                   const std::string&, 
                   const std::string&, 
                   const boost::filesystem::path&);
        template<typename T, typename U>
        int32_t* fetch_ccd(const std::string&, 
                           const std::string&, 
                           const std::string&, 
                           const boost::filesystem::path&, 
                           std::function<U>);
        
        void decode_science(IMS::Science&, 
                            int32_t**, 
                            const char&, 
                            const int32_t&);
        void decode_wavefront(IMS::WaveFront&, 
                              int32_t**, 
                              const char&, 
                              const int32_t&);

        void get_naxes(const IMS::Source&, long*);
        bool has_image(const std::string&);

    private:
        IMS::Store _store;
        FitsFormatter _formatter;
};

class PixelArray { 
    public:
        PixelArray(const int&, const int&);
        ~PixelArray();
        int32_t** get();
    private:
        int32_t** _arr;
        int _d1, _d2;
};

class StripeArray { 
    public: 
        StripeArray(const int&);
        ~StripeArray();
        IMS::Stripe* get();
    private:
        IMS::Stripe* _arr;
};
