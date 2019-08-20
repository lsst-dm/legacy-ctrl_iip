#include <functional>
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
        int32_t* fetch_ccd(std::string, std::string, std::string, const boost::filesystem::path&, std::function<U>);
        
        void decode_science(IMS::Science&, int32_t**, const char&, const int32_t&);
        void decode_wavefront(IMS::WaveFront&, int32_t**, const char&, const int32_t&);

        void get_naxes(const IMS::Source&, long*);
        bool has_image(const std::string&);

    private:
        IMS::Store _store;
        std::string _prefix;
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
