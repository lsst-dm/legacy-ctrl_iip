#include "forwarder/DAQFetcher.h"

StripeArray::StripeArray(const int& len) { 
    _arr = new IMS::Stripe[len];
}

StripeArray::~StripeArray() { 
    delete[] _arr;
}

IMS::Stripe* StripeArray::get() { 
    return _arr;
}
