#ifndef MINIFORWARDER_H
#define MINIFORWARDER_H

#include <map>
#include <functional>
#include <boost/filesystem.hpp>
#include <yaml-cpp/yaml.h>

#include "core/IIPBase.h"
#include "core/SimplePublisher.h"
#include "core/Scoreboard.h"

#include "forwarder/MessageBuilder.h"
#include "forwarder/HeaderFetcher.h"
#include "forwarder/DAQFetcher.h"
#include "forwarder/Formatter.h"
#include "forwarder/FileSender.h"

class miniforwarder : public IIPBase {
    public:
        miniforwarder();
        ~miniforwarder();

        void on_message(const std::string&);
        void run();

        void health_check(const YAML::Node&);
        void xfer_params(const YAML::Node&);
        void header_ready(const YAML::Node&);
        void end_readout(const YAML::Node&);

        void assemble(const std::string&);
        void publish_ack(const YAML::Node&);
        boost::filesystem::path create_dir(const std::string&, const std::string&);

    private:
        std::string _name;
        std::string _consume_q;
        std::string _amqp_url;

        boost::filesystem::path _header_path;
        boost::filesystem::path _fits_path;

        std::map<const std::string, std::function<void (const YAML::Node&)> > _actions;

        SimplePublisher* _pub;
        MessageBuilder _builder;
        HeaderFetcher _hdr;
        DAQFetcher _daq;
        FitsFormatter _fmt;
        Scoreboard _db;
        FileSender _sender;
};

#endif
