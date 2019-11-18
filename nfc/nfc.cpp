/////////////////////////
// INCLUDE STATEMENTS //
///////////////////////

// For console output
#include <iostream>
// For sleep
#include <chrono>
#include <thread>
#include <sstream>
#include <fstream>
#include <string>
#include <unistd.h>
#include <ctime>
#include "mqtthelper.h"
// For using NFC
#include "matrix_nfc/nfc.h"
#include "matrix_nfc/nfc_data.h"
#include "matrix_hal/matrixio_bus.h"

char ADDRESS[] = "localhost:1883";
char CLIENTID[] = "default";
char TOPIC[] = "payment/start";
char topic_pub_status[] = "payment/status";

int QOS =  0;


int payment(std::string user_id,double amount){
  std::ofstream file("temp.txt");
  std::fstream myfile ("data.txt");
  std::string id;
  double balance;
  int flag = 0;
  if(myfile.is_open()) {
    while(1)
  {

    myfile >>id >> balance;
    if( myfile.eof() ) break;
    if (id.compare(user_id)==0){
      if(balance>=amount){
      flag = 1;
      
      balance-=amount;
    }
    }
    file<<id<<" "<<balance<<std::endl;
  }
 }

  myfile.close();
  file.close();
  rename("temp.txt","data.txt");
  if (flag == 1){
   return 1;
  }
  else{
    return 0;
  }

}

int scan(double amount){
  matrix_hal::NFC nfc;
    matrix_hal::NFCData nfc_data;
  std::cout << "[NFC]: NFC started!" << std::endl;
  int sucess = 0;
  auto past_time = std::chrono::system_clock::now();
  auto current_time = std::chrono::system_clock::now();
  std::chrono::duration<double> duration = (current_time-past_time);
  while(duration.count()<60){
    current_time = std::chrono::system_clock::now();
    duration = current_time-past_time;
    nfc.Activate();
    nfc.ReadInfo(&nfc_data.info);
    nfc.Deactivate();

    if (nfc_data.info.recently_updated) {

        std::cout << "[NFC] : " + nfc_data.info.ToString() << std::endl;
    
        std::string user_id = nfc_data.info.UIDToHex();

        sucess = payment(user_id, amount);
        
        break;
    }
    std::this_thread::sleep_for(std::chrono::microseconds(10000));

}
return sucess;
}


int main() {
    ////////////////////
    // INITIAL SETUP //
    //////////////////

    // Setting up HAL bus
    matrix_hal::MatrixIOBus bus;
    if (!bus.Init()) return false;



    // Setting up NFC
    

    initMqtt(ADDRESS,CLIENTID,TOPIC,QOS);
      int success = 0;
     while(1){
       if(msg>0){
        
         success = scan(msg);
         msg = 0;
         std::cout<<"[NFC] : success"<<success<<std::endl;
    
       std::string s = std::to_string(success);
      char const *suc = s.c_str(); 
   publishStatus(topic_pub_status,(char*)suc);
   }

     }
    return 0;
}
