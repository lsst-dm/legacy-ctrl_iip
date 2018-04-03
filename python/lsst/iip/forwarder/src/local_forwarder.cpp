/////////////////////////////////////////////////////////////////
//

#include <sys/stat.h> 
#include <errno.h>
#include <dirent.h>
#include <stdio.h>
#include "Exceptions.h"

////////////////////////////////////////////////////////////////////////////////
// @ FORMAT THREAD
////////////////////////////////////////////////////////////////////////////////
void Forwarder::process_header_ready(Node n) { 
    try { 
        string main_header_dir = this->Work_Dir + "/header"; 
        const int dir = mkdir(main_header_dir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR); 
        if (dir == -1 && errno != 17) { 
            throw L1CannotCreateDirError("In process_header_ready, forwarder cannot create directory in: " + main_header_dir); 
        } 

        if (!n["FILENAME"]) { 
            throw L1YamlKeyError("In process_header_ready, forwarder cannot find message params: FILENAME"); 
        } 

        string path = n["FILENAME"].as<string>(); 
        string img_id = n["IMAGE_ID"].as<string>(); 
        int img_idx = path.find_last_of("/"); 
        /** 
        int dot_idx = path.find_last_of("."); 
        int num_char = dot_idx - (img_idx + 1); // offset +1
        string img_id = path.substr(img_idx + 1, num_char); 
        */

        string sub_dir = main_header_dir + "/" + img_id; 
        const int dir_cmd = mkdir(sub_dir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR);  
        if (dir_cmd == -1 && errno != 17) { 
            throw L1CannotCreateDirError("In process_header_ready, forwarder cannot create sub_directory in: " + sub_dir); 
        } 

        // scp -i ~/.ssh/from_efd felipe@141.142.23x.xxx:/tmp/header/IMG_ID.header to /tmp/header/IMG_ID/IMG_ID.header
        ostringstream cp_cmd; 
        cp_cmd << "scp -i ~/.ssh/from_efd "
               << path
               << " " 
               << sub_dir
               << "/"; 
        int scp_cmd = system(cp_cmd.str().c_str()); 
        if (scp_cmd == 256) { 
            throw L1CannotCopyFileError("In process_header_ready, forwarder cannot copy file: " + cp_cmd.str()); 
        } 

        string img_idx_wheader = path.substr(img_idx + 1);  
        string header_path = sub_dir + "/" + img_idx_wheader;

        Emitter msg; 
        msg << BeginMap; 
        msg << Key << "MSG_TYPE" << Value << "FORMAT_HEADER_READY"; 
        msg << Key << "IMAGE_ID" << Value << img_id; 
        msg << Key << "FILENAME" << Value << header_path; 
        msg << EndMap; 
        FWDR_to_format_pub->publish_message(this->format_consume_queue, msg.c_str()); 
        cout << "[STATUS] Finished copying header file from " << path << " . File is in " << sub_dir << endl; 
    } 
    catch (L1YamlKeyError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 2; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (L1CannotCreateDirError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 20; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (L1CannotCopyFileError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 21; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::format_process_end_readout(Node node) { 
    cout << "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" << endl; 
    cout << "[f] fper" << endl;
    try { 
        string image_id = node["IMAGE_ID"].as<string>(); 
        this->readout_img_ids.push_back(image_id); 
        this->format_look_for_work(); 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::format_get_header(Node node) { 
    cout << "[f] fgh" << endl; 
    try { 
        string image_id = node["IMAGE_ID"].as<string>(); 
        string filename = node["FILENAME"].as<string>(); 
        cout << "[x] " << image_id << ": " << filename << endl;
        this->header_info_dict[image_id] = filename; 
        this->format_look_for_work(); 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::format_assemble_img(Node n) {
    cout << "[f] fai" << endl; 
    try { 
        string img_id = n["IMAGE_ID"].as<string>(); 
        string header = n["HEADER"].as<string>(); 
        // create dir  /mnt/ram/FITS/IMG_10
        string fits_dir = Work_Dir + "/FITS"; 
        cout << "[x] fits_dir: " << fits_dir << endl; 
        const int dir = mkdir(fits_dir.c_str(), S_IRUSR | S_IWUSR | S_IXUSR); 
        format_write_img(img_id, header);
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
}


char* Forwarder::format_read_img_segment(const char *file_path) { 
    try { 
        fstream img_file(file_path, fstream::in | fstream::binary); 
        long len = WIDTH * HEIGHT; 
        char *buffer = new char[len]; 
        img_file.seekg(0, ios::beg); 
        img_file.read(buffer, len); 
        img_file.close();
        return buffer;
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

unsigned char** Forwarder::format_assemble_pixels(char *buffer) { 
    try { 
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
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::format_write_img(string img, string header) { 
    cout << "[x] fwi" << endl;
    try { 
        long len = WIDTH * HEIGHT;
        int bitpix = LONG_IMG; 
        long naxis = 2;
        long naxes[2] = { WIDTH, HEIGHT }; 
        long fpixel = 1; 
        long nelements = len; 
        int status = 0; 
        int hdunum = 2;
        int nkeys; 
        char card[FLEN_CARD]; 
        fitsfile *iptr, *optr; 

        // /mnt/ram/IMG_31
        string img_path = Work_Dir + "/" + img;
        string header_path = header;
        string destination = Work_Dir + "/FITS/" + img + ".fits";
        cout << "[x] header: " << header_path << endl; 
        cout << "[x] destination:" << destination << endl;
        cout << "[x] Image files are in: " << img_path << endl; 

        fits_open_file(&iptr, header_path.c_str(), READONLY, &status); 
        fits_create_file(&optr, destination.c_str(), &status); 
        fits_copy_hdu(iptr, optr, 0, &status); 

        vector<string> file_names = format_list_files(img_path); 
        vector<string>::iterator it; 
        for (it = file_names.begin(); it != file_names.end(); it++) { 
            string img_segment = img_path + "/" + *it; 
            char *img_buffer = format_read_img_segment(img_segment.c_str());
            unsigned char **array = format_assemble_pixels(img_buffer); 

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
        fits_close_file(iptr, &status); 
        fits_close_file(optr, &status); 

        cout << "end of fwi" << endl;
        format_send_completed_msg(img);
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

vector<string> Forwarder::format_list_files(string path) { 
    try { 
        struct dirent *entry; 
        DIR *dir  = opendir(path.c_str()); 
        vector<string> file_names; 
        while (entry  = readdir(dir)) { 
            string name = entry->d_name;
            if (strcmp(name.c_str(), ".") && strcmp(name.c_str(), "..")) { 
                file_names.push_back(name); 
            }
        } 

        sort(file_names.begin(), file_names.end()); 
        closedir(dir);
        return file_names; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::format_send_completed_msg(string image_id) { 
    cout << "[f] fscm" << endl;
    try { 
        Emitter msg; 
        msg << BeginMap; 
        msg << Key << "MSG_TYPE" << Value << "FORWARD_END_READOUT"; 
        msg << Key << "IMAGE_ID" << Value << image_id; 
        msg << EndMap; 
        fmt_pub->publish_message(this->forward_consume_queue, msg.c_str()); 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::format_look_for_work() { 
    cout << "[f] flfw" << endl;
    try { 
        vector<string>::iterator it;
        map<string, string>::iterator mit;  
        map<string, string>::iterator tid; 
        cout << "readout SIZE: " << readout_img_ids.size() << endl;
        if (this->readout_img_ids.size() != 0 && this->header_info_dict.size() != 0) { 
            cout << "[x] img data exists" << endl; 
            for (it = this->readout_img_ids.begin(); it != this->readout_img_ids.end(); ) { 
                string img_id = *it; 
                mit = this->header_info_dict.find(img_id); 
                if (mit != this->header_info_dict.end()) { 
                    this->readout_img_ids.erase(it); 
                    string header_filename = this->header_info_dict[img_id]; 
                    this->header_info_dict.erase(mit); 

                    // do the work 
                    Node n; 
                    n["IMAGE_ID"] = img_id; 
                    n["HEADER"] = header_filename; 
                    format_assemble_img(n); 
                } 
                else it++; 
            } 
        } 
        else if (this->readout_img_ids.size() == 0 || this->header_info_dict.size() == 0) { 
            cout << "[x] no img data" << endl; 
            return; 
        } 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 


///////////////////////////////////////////////////////////////////////////////
// FORWARD THREAD 
///////////////////////////////////////////////////////////////////////////////
void Forwarder::forward_process_end_readout(Node n) { 
    try { 
        string img_id = n["IMAGE_ID"].as<string>(); 
        string img_path = this->Work_Dir + "/FITS/" + img_id + ".fits"; 
        string dest_path = this->Target_Location + "/" + img_id + ".fits"; 
        cout << "[STATUS] file is copied from " << img_path << " to " << dest_path << endl; 
      
        size_t find_at = dest_path.find("@"); 
        ostringstream bbcp_cmd; 
        if (find_at != string::npos) { 
            bbcp_cmd << "scp -i ~/.ssh/from_efd ";
        } 
        else { 
            bbcp_cmd << "cp "; 
        } 
        bbcp_cmd << img_path
                 << " " 
                 << dest_path; 
        int bbcp_cmd_status = system(bbcp_cmd.str().c_str()); 
        if (bbcp_cmd_status == 256) { 
            throw L1CannotCopyFileError("In forward_process_end_readout, forwarder cannot copy file: " + bbcp_cmd.str()); 
        } 
        this->finished_image_work_list.push_back(img_id);
        cout << "[X] READOUT COMPLETE." << endl;
    } 
    catch (L1CannotCopyFileError& e) { 
        int ERROR_CODE = ERROR_CODE_PREFIX + 21; 
        cerr << e.what() << endl; 
        cerr << "Forwarder encountering error code: " << to_string(ERROR_CODE) << endl; 
    } 
    catch (exception& e) { 
        cerr << e.what() << endl; 
    } 
} 

void Forwarder::forward_process_take_images_done(Node n) { 
    cout << "get here" << endl;
    ostringstream message;
    string ack_id = n["ACK_ID"].as<string>();
    string reply_queue = n["REPLY_QUEUE"].as<string>();
    string msg_type = "AR_FWDR_TAKE_IMAGES_DONE_ACK ";
    string ack_bool = "True";
  
    Emitter msg; 
    msg << BeginMap; 
    msg << Key << "MSG_TYPE" << Value << msg_type; 
    msg << Key << "COMPONENT" << Value << this->Component; 
    msg << Key << "ACK_ID" << Value << ack_id; 
    msg << Key << "ACK_BOOL" << Value << ack_bool; 
    msg << Key << "RESULT_SET" << Value << Flow; 
        msg << BeginMap; 
        msg << Key << "FILENAME_LIST" << Value << Flow << finished_image_work_list; 
        msg << Key << "CHECKSUM_LIST" << Value << Flow << checksum_list;  
        msg << EndMap; 
    msg << EndMap; 
    cout << "[x] tid msg: " << endl; 
    cout << msg.c_str() << endl;
  
    this->fwd_pub->publish_message(reply_queue, msg.c_str());
    cout << "msg is replied to ..." << reply_queue << endl;
} 

///////////////////////////////////////////////////////////////////////////////
// Forward part  done
///////////////////////////////////////////////////////////////////////////////

int main() {
    Forwarder *fwdr = new Forwarder();
    fwdr->run();
    while(1) {
    }
}


