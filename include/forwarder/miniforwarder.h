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

#ifndef MINIFORWARDER_H
#define MINIFORWARDER_H

#include <map>
#include <functional>
#include <boost/filesystem.hpp>
#include <yaml-cpp/yaml.h>

#include "core/IIPBase.h"
#include "core/SimplePublisher.h"

#include "forwarder/Scoreboard.h"
#include "forwarder/MessageBuilder.h"
#include "forwarder/HeaderFetcher.h"
#include "forwarder/DAQFetcher.h"
#include "forwarder/Formatter.h"
#include "forwarder/FileSender.h"
#include "forwarder/ReadoutPattern.h"

class miniforwarder : public IIPBase {
    public:
        miniforwarder(const std::string& config, 
                      const std::string& log);
        ~miniforwarder();

        void on_message(const std::string&);
        void run();

        void health_check(const YAML::Node&);
        void xfer_params(const YAML::Node&);
        void header_ready(const YAML::Node&);
        void end_readout(const YAML::Node&);
        void process_ack(const YAML::Node&);

        void assemble(const std::string&);
        void publish_ack(const YAML::Node&);
        void publish_xfer_complete(const std::string& to,
                                   const std::string& session_id,
                                   const std::string& job_num);
        boost::filesystem::path create_dir(const std::string&);
        bool check_valid_board(const std::string& raft, const std::string& ccd);
        void register_fwd();

    private:
        std::string _name;
        std::string _consume_q;
        std::string _archive_q;
        std::string _amqp_url;
        std::string _partition;

        boost::filesystem::path _header_path;
        boost::filesystem::path _fits_path;

        std::map<const std::string, std::function<void (const YAML::Node&)> > _actions;
        std::vector<std::string> _daq_locations;

        std::unique_ptr<SimplePublisher> _pub;
        std::unique_ptr<Scoreboard> _db;
        std::unique_ptr<DAQFetcher> _daq;

        MessageBuilder _builder;
        HeaderFetcher _hdr;
        FitsFormatter _fmt;
        FileSender _sender;
        ReadoutPattern _readoutpattern;
};

#endif
