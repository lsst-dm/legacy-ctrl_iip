#include <functional>
#include <vector>
#include <boost/filesystem.hpp>

#include "ims/Store.hh"
#include "ims/Source.hh"
#include "ims/WaveFront.hh"
#include "ims/Science.hh"

#include "Formatter.h"

class DAQFetcher { 
    public:
        DAQFetcher(const char*, std::string);
        ~DAQFetcher();

        void fetch(std::string, std::string, std::string, std::string, const boost::filesystem::path&);
        template<typename T, typename U>
        void fetch_ccd(std::string, std::string, std::string, const boost::filesystem::path&, std::function<U>);
        
        void decode_science(IMS::Science&, std::vector<std::vector<int32_t>>&, const char&, const int32_t&);
        void decode_wavefront(IMS::WaveFront&, std::vector<std::vector<int32_t>>&, const char&, const int32_t&);

        void get_naxes(const IMS::Source&, long*);
        bool has_image(const std::string&);

    private:
        IMS::Store _store;
        std::string _prefix;
        FitsFormatter _formatter;
};

class PixelArray { 
    public:
        PixelArray(const std::vector<std::vector<int32_t>>&); 
        ~PixelArray();
        int32_t** get();
    private:
        int32_t _d1, _d2;
        int32_t** _arr;
};

class StripeArray { 
    public: 
        StripeArray(const int&);
        ~StripeArray();
        IMS::Stripe* get();
    private:
        IMS::Stripe* _arr;
};
