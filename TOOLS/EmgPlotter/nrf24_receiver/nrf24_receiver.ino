//Include Libraries
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>


//create an RF24 object
RF24 radio(9, 10);  // CE, CSN

//address through which two modules communicate.
const byte address[6] = "00002";


void setup()
{
  while (!Serial);
    Serial.begin(500000);
  
  radio.begin();
  radio.setChannel(105);
  radio.setPALevel (RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  radio.setRetries(0,0);
  radio.setAutoAck (false);
  
  //set the address
  radio.openReadingPipe(0, address);
  
  //Set module as receiver
  radio.startListening();
}


void readval(){
    char text[32] = {0};
    radio.read(&text, sizeof(text));
    Serial.print(text);
}


void loop()
{
  readval();
}
