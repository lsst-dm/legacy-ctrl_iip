/* Standard C++ includes */
#include <stdlib.h>
#include <string.h>
#include <iostream>
#include "fitsio.h"

/*
  Include directly the different
  headers from cppconn/ and mysql_driver.h + mysql_util.h
  (and mysql_connection.h). This will reduce your build time!
*/

#include <cppconn/driver.h>
#include <cppconn/exception.h>
#include <cppconn/resultset.h>
#include <cppconn/statement.h>
#include <cppconn/prepared_statement.h>

using namespace std;


int main(int argc, char *argv[])
{
    cout << endl;
    cout << "Start MySQL.... with insert and query" << endl;
    try
    {
        sql::Driver *driver;
        sql::Connection *con;
        sql::ResultSet *res;
        sql::Statement *stmt;
        sql::PreparedStatement *pstmt;

        DB = "tefd";

        // log in to database
        driver = get_driver_instance();
        con = driver->connect("tcp://141.142.210.138", "root", "Zhuzhanyansb1");
        con->setSchema(DB);

        // add one element img 298
        string fields[7] = {"BITPIX", "IMAGEN", "NAXIS", "CCDN", "FILTERN", "TILEN", "EXPSEC"};

        stmt = con->createStatement();
        stmt->execute("CREATE TABLE 298(BITPIX INT, IMAGEN INT, NAXIS INT, CCDN INT, FILTERN VARCAR(1), TILEN INT, EXPSEC INT)");
        delete stmt;

        pstmt = con->prepareStatement("INSERT INTO test(BITPIX, IMAGEN, NAXIS, CCDN, FILTERN, TILEN, EXPSEC) VALUES (?,?,?,?,?,?,?)");
        for (int i = 0; i < 9; i++) {
            pstmt->setInt(1, 32);
            pstmt->setInt(2, 298);
            pstmt->setInt(3, 2);
            pstmt->setInt(4, i);
            pstmt->setString(5, "A");
            pstmt->setInt(6, 345);
            pstmt->setInt(7, 5);
            pstmt->executeUpdate();
        }
        delete pstmt;

        // create fits file
        fitsfile * fptr;
        int status = 0;

        fits_create_file(&fptr, argv[1] , &status);

        // select one image, return a linked list

        stmt = con->createStatement();
        res = stmt->executeQuery("SELECT * FROM 298");

        /*
            i. BITPIX=32
            ii. IMAGEN=(same as table name...same for each row)
            iii.NAXIS=2
            iv. CCDN
            v. FILTERN=(A or B or C or D)
            vi. TILEN=(an int less than 1000...same for each row)
            vii. EXPSEC=(an int 1 thru 15, same for each row)
        */

        while (res->next()) {
            // res read by colomns 
            for(int j = 0; j < 9; j++){
                for(int i = 0; i < 16; i++){
                    // for every ccd add 16 AMP
                    // maybe use fits_write_key
                }
            }
        }
        delete res;
        delete stmt;
        delete con;

    } 
    catch (sql::SQLException &e) 
    {
        cout << "# ERR: SQLException in " << __FILE__;
        cout << "(" << __FUNCTION__ << ") on line " << __LINE__ << endl;
        cout << "# ERR: " << e.what();
        cout << " (MySQL error code: " << e.getErrorCode();
        cout << ", SQLState: " << e.getSQLState() << " )" << endl;
    }

    cout << endl;
    return EXIT_SUCCESS;
}