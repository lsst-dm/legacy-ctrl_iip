#include <iostream>
#include <fstream> 
#include <string>
#include <sys/stat.h>
#include "fitsio.h"
#include "Formatter.h"

#define SECONDARY_HDU 2
#define HEIGHT 512
#define WIDTH 2048
#define RAFT 2 // FIXME
#define CCD 2
#define SEGMENT 2

using namespace std; 
using namespace YAML;
using funcptr = void (Formatter::*)(Node); 

map<string, funcptr> action_handler = { 
    { "START_FORMAT", &Formatter::assemble_img }, 
}; 

Formatter::Formatter() { 
    Node config_file = LoadFile("ForwarderCfg.yaml"); 
    Node root = config_file["ROOT"]; 
    string user = root["FORMAT_USER"].as<string>(); 
    string pwd = root["FORMAT_USER_PASSWD"].as<string>(); 
    string user_pub = root["FORMAT_USER_PUB"].as<string>(); 
    string pwd_pub = root["FORMAT_USER_PUB_PASSWD"].as<string>(); 
    string broker_addr = root["BASE_BROKER_ADDR"].as<string>(); 
    forward_consume_queue = root["FORWARD_CONSUME_QUEUE"].as<string>();
    format_consume_queue = root["FORMAT_CONSUME_QUEUE"].as<string>(); 

    work_dir = root["WORK_DIR"].as<string>();
    consumer_addr = "amqp://" + user + ":" + pwd + "@" + broker_addr; 
    publisher_addr = "amqp://" + user_pub + ":" + pwd_pub + "@" + broker_addr; 
} 

Formatter::~Formatter() { 
    /**
    delete buffer;
    delete array;
    delete fmt_publisher; 
    delete fmt_consumer;
    */
} 

void Formatter::setup_publisher() { 
    fmt_publisher = new SimplePublisher(publisher_addr); 
} 

void Formatter::setup_consumer() { 
    fmt_consumer = new Consumer(consumer_addr, format_consume_queue); 
} 

void Formatter::run() { 
    callback<Formatter> on_msg = &Formatter::on_message; 
    fmt_consumer->run<Formatter>(this, on_msg); 
} 

void Formatter::on_message(string message) { 
    Node node = Load(message); 
    string message_value = node["MSG_TYPE"].as<string>(); 
    funcptr action = action_handler[message_value]; 
    (this->*action)(node); 
} 

char* Formatter::read_img_segment(const char *file_path) { 
    fstream img_file(file_path, fstream::in | fstream::binary); 
    long len = WIDTH * HEIGHT; 
    char *buffer = new char[len]; 
    img_file.seekg(0, ios::beg); 
    img_file.read(buffer, len); 
    img_file.close();
    return buffer;
} 

unsigned char** Formatter::assemble_pixels(char *buffer) { 
    unsigned char **array = new unsigned char*[HEIGHT]; 
    array[0] = (unsigned char *) malloc( WIDTH * HEIGHT * sizeof(unsigned char)); 

    for (int i = 1; i < HEIGHT; i++) { 
        array[i] = array[i-1] + WIDTH; 
    } 

    for (int j = 0; j < HEIGHT; j++) {
        for (int i = 0; i < WIDTH; i++) {
            array[j][i]= buffer[i+j]; 
        } 
    }
    return array;
} 

void Formatter::write_img(string img_path, string header_path, string destination) { 
    long len = WIDTH * HEIGHT;
    int bitpix = BYTE_IMG; 
    long naxis = 2;
    long naxes[2] = { WIDTH, HEIGHT }; 
    long fpixel = 1; 
    long nelements = len; 
    int status = 0; 
    int hdunum = 2;
    int nkeys; 
    char card[FLEN_CARD]; 
    fitsfile *iptr, *optr; 

    fits_open_file(&iptr, header_path, READONLY, &status); 
    fits_create_file(&optr, destination, &status); 
    fits_copy_hdu(iptr, optr, 0, &status); 

    for (int raft = 0; raft < RAFT; raft++) {
        for (int ccd = 0; ccd < CCD; ccd++) { 
            for (int segment = 0; segment < SEGMENT; segment++) { 
                string img_segment = img_path + "/" + \
                                     "raft-" + to_string(raft) + "_" + \
                                     "ccd-" + to_string(ccd) + "_" + \
                                     "segment-" + to_string(segment);
                cout << img_segment << endl;
                char *img_buffer = read_img_segment(img_segment.c_str());
                unsigned char **array = assemble_pixels(img_buffer); 

                fits_movabs_hdu(iptr, hdunum, NULL, &status); 
                fits_create_img(optr, bitpix, naxis, naxes, &status); 
                fits_write_img(optr, TBYTE, fpixel, nelements, array[0], &status); 

                fits_get_hdrspace(iptr, &nkeys, NULL, &status); 
                for (int i = 1; i <= nkeys; i++) { 
                    fits_read_record(iptr, i, card, &status); 
                    fits_write_record(optr, card, &status); 
                }
                hdunum++;
            }
        }
    }
    fits_close_file(iptr, &status); 
    fits_close_file(optr, &status); 

    send_completed_msg(destination);
} 

void Formatter::assemble_img(Node n) {
    string img = n["IMG_NAME"].as<string>(); 
    string header_path = n["HEADER_PATH"].as<string>(); 
    string img_path = work_dir + img;

    // create dir 
    string destination = work_dir + "FITS/" + img; 
    write_img(img_path, header_path, destination);
}

void Formatter::send_completed_msg(string directory) { 
    string msg = "{ MSG_TYPE: FORMAT_DONE, " + \
                 "  DIRECOTRY: " + directory + "}"; 
    fmt_publisher->publish_message(forward_consume_queue, msg); 
} 

int main() { 
    Formatter fmt; 
    fmt.run();
    return 0;
} 
