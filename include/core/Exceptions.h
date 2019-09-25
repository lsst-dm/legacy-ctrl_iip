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

#ifndef EXCEPTIONS_H
#define EXCEPTIONS_H

#include <iostream> 
#include <exception>

/**
 * Exception classes for CTRL_IIP package
 */
namespace L1 { 
    /**
     * Base exception class inherited from `std::exception` for CTRL_IIP 
     * package that will be extended further to throw custom exceptions.
     */
    class L1Exception: public std::exception { 
        public: 
            /**
             * Construct Base Exception
             *
             * @param msg error message
             */
            L1Exception(const std::string& msg){
                errormsg = msg; 
            } 

            /**
             * virutal method for overwriting std::exception throw method
             *
             * @return error message
             */
            virtual const char* what() const throw() { 
                return errormsg.c_str(); 
            } 
        private:
            std::string errormsg; 

    }; 

    /**
     * Throws when YAML-CPP library throws internal exception
     */
    class YamlKeyError : public L1Exception { 
        public: 
            YamlKeyError(const std::string& msg) : L1Exception(msg) {}
    }; 

    /**
     * Throws when `RabbitConnection` cannot connect to RabbitMQ server
     */
    class RabbitConnectionError : public L1Exception { 
        public: 
            RabbitConnectionError(const std::string& msg) : L1Exception(msg) {}
    }; 

    /**
     * Throws when SimplePublisher cannot connect to RabbitMQ Server or
     * cannot publish messages to queue
     */
    class PublisherError : public L1Exception { 
        public: 
            PublisherError(const std::string& msg) : L1Exception(msg) {}
    }; 

    /**
     * Throws when Consumer cannot connect to RabbitMQ Server or cannot
     * consume messages
     */
    class ConsumerError : public L1Exception { 
        public: 
            ConsumerError(const std::string& msg) : L1Exception(msg) {}
    }; 

    /**
     * Throws when application cannot create directory
     */
    class CannotCreateDir: public L1Exception { 
        public: 
            CannotCreateDir(const std::string& msg) : L1Exception (msg) {} 
    }; 

    /**
     * Throws when application cannot copy file(most likely bbcp)
     */
    class CannotCopyFile: public L1Exception { 
        public: 
            CannotCopyFile(const std::string& msg) : L1Exception(msg) {} 
    }; 

    /**
     * Throws when `HeaderFetcher` cannot fetch header file from HeaderService
     */
    class CannotFetchHeader: public L1Exception { 
        public: 
            CannotFetchHeader(const std::string& msg) : L1Exception(msg) {} 
    }; 

    /**
     * Throws when `CURLHandle` cannot create handle for HTTP connection
     */
    class NoCURLHandle: public L1Exception { 
        public: 
            NoCURLHandle(const std::string& msg) : L1Exception(msg) {} 
    }; 

    /**
     * Throws when Cfitsio library related function calls return error status
     */
    class CfitsioError: public L1Exception { 
        public: 
            CfitsioError(const std::string& msg) : L1Exception(msg) {} 
    }; 

    /**
     * Throws when forwarder cannot assemble fitsfile with header file
     */
    class CannotFormatFitsfile: public L1Exception { 
        public: 
            CannotFormatFitsfile(const std::string& msg) : L1Exception(msg) {} 
    }; 

    /**
     * Throws when forwarder cannot fetch pixel data from DAQ hardware
     */
    class CannotFetchPixel: public L1Exception { 
        public: 
            CannotFetchPixel(const std::string& msg) : L1Exception(msg) {} 
    }; 

    /**
     * Throws when Scoreboard cannot find key inside its data structure to
     * operate on
     */
    class KeyNotFound: public L1Exception { 
        public: 
            KeyNotFound(const std::string& msg) : L1Exception(msg) {} 
    }; 

    class RedisError: public L1Exception { 
        public: 
            RedisError(const std::string& msg) : L1Exception(msg) {} 
    }; 

    class InvalidReadoutPattern: public L1Exception { 
        public: 
            InvalidReadoutPattern(const std::string& msg) : L1Exception(msg) {}
    }; 
};

#endif
