// Include Libraries
// Documents > Arduino> NRF_Teensy > latest version
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <ADC.h>
#include <ADC_util.h>

// Define Channels to be used
//#define CHANNEL1
#define CHANNEL2
//#define CHANNEL3
//#define CHANNEL4


/* Global Vairables */
const byte address[6] = "00002"; // address through which two modules communicate.
int LED = A6;
char sendMe[32];
String st1,st2,st3,st4;
int out;

#ifdef CHANNEL1
  const int CH1 = A1; // ADC0
  int CH1_value;
#endif

#ifdef CHANNEL2
  const int CH2 = A2; // ADC0
  int CH2_value;
#endif

#ifdef CHANNEL3
  const int CH3 = A3; // ADC0
  int CH3_value;
#endif

#ifdef CHANNEL4
  const int CH4 = A4; // ADC0
  int CH4_value;
#endif

/* Global Objects */
RF24 radio(9, 10);  // CE, CSN

ADC *adc = new ADC();


/* Setup function */
void setup()
{
  #ifdef CHANNEL1
    pinMode(CH1, INPUT);
  #endif
  #ifdef CHANNEL2
    pinMode(CH2, INPUT);
  #endif
  #ifdef CHANNEL3
    pinMode(CH3, INPUT);
  #endif
  #ifdef CHANNEL4
    pinMode(CH4, INPUT);
  #endif
  pinMode(LED, OUTPUT);
  
  adc->adc0->setAveraging(32); // set number of averages
  adc->adc0->setResolution(16); // set bits of resolution
  adc->adc0->setConversionSpeed(ADC_CONVERSION_SPEED::MED_SPEED); 
  adc->adc0->setSamplingSpeed(ADC_SAMPLING_SPEED::HIGH_SPEED); 
  Serial.begin(500000);
 
  radio.begin();
  radio.setChannel(105);
  radio.setPALevel (RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  radio.setRetries(0,0);
  radio.setAutoAck (false);
  
  // set the address
  radio.openWritingPipe(address);
  
  // Set module as transmitter
  radio.stopListening();

  delay (500);
}


/* IIR low pass DSP filter at cut-off frequency 100Hz
  yv[2] =   (b0 * xv[2]) + (b1 * xv[1]) + (b2 * xv[0]) - (a1 * yv[1]) - (a2 * yv[0]);
  Helps to remove noise from raw EMG signal
*/
unsigned int lpf100(float in) // sample rate = 1000 fc = 100hz, 2nd order
{
  static float xv[3], yv[3];
  xv[0] = xv[1]; xv[1] = xv[2];
  xv[2] = in;
  yv[0] = yv[1]; yv[1] = yv[2];
  yv[2] = (0.06745228 * xv[2]) + (0.13490457 * xv[1]) + (0.06745228 * xv[0]) + (1.14292982 * yv[1]) - (0.41273895 * yv[0]);
  return out = yv[2];
}


/* IIR high pass DSP filter at cut-off frequency 5Hz */
/* unsigned int hpf005 (float in) // sample rate = 1000 fc = 5hz, 2nd order
{
  static float xv[3], yv[3];
  xv[0] = xv[1]; xv[1] = xv[2];
  xv[2] = in;
  yv[0] = yv[1]; yv[1] = yv[2];
  yv[2] = (0.97802727 * xv[2]) + (-1.95605454 * xv[1]) + (0.97802727 * xv[0]) - (-1.95557182 * yv[1]) - (0.95653726 * yv[0]);
  return out = yv[2];
} */


/* Loop function */
void loop()
{
  String ini = "a$";

  ////////////////////////////////////// channel 1 /////////////////////////////////////
  #ifdef CHANNEL1
    CH1_value = lpf100((float)adc->adc0->analogRead(CH1));

    ///// if PGA is used and gain = 16 :
    //CH1_PGA = ((CH1_value - 32500) * 16) + 32500;

    if (CH1_value < 10){
      st1 = "0000" + String (CH1_value);
    }
    else if (10< CH1_value && CH1_value <100){
      st1 = "000" + String (CH1_value);
    }
    else if (100 < CH1_value && CH1_value < 1000){
      st1 = "00" + String (CH1_value);
    }
    else if (1000 < CH1_value && CH1_value < 10000){
      st1 = "0" + String (CH1_value);
    }
    else {
      st1 =  String (CH1_value);
    }
  #endif

  ////////////////////////////////////// channel 2 /////////////////////////////////////
  #ifdef CHANNEL2
    CH2_value = lpf100((float)adc->adc0->analogRead(CH2));

    if (CH2_value < 10){
      st2 = "0000" + String (CH2_value);
    }
    else if (10< CH2_value && CH2_value <100){
      st2 = "000" + String (CH2_value);
    }
    else if (100 < CH2_value && CH2_value < 1000){
      st2 = "00" + String (CH2_value);
    }
    else if (1000 < CH2_value && CH2_value < 10000){
      st2 = "0" + String (CH2_value);
    }
    else {
      st2 =  String (CH2_value);
    }
  #endif

  ////////////////////////////////////// channel 3 /////////////////////////////////////
  #ifdef CHANNEL3
    CH3_value = lpf100((float)adc->adc0->analogRead(CH3));

    if (CH3_value < 10){
      st3 = "0000" + String (CH3_value);
    }
    else if (10< CH3_value && CH3_value <100){
      st3 = "000" + String (CH3_value);
    }
    else if (100 < CH3_value && CH3_value < 1000){
      st3 = "00" + String (CH3_value);
    }
    else if (1000 < CH3_value && CH3_value < 10000){
      st3 = "0" + String (CH3_value);
    }
    else {
      st3 =  String (CH3_value);
    }
  #endif

  ////////////////////////////////////// channel 4 /////////////////////////////////////
  #ifdef CHANNEL4
    CH4_value = lpf100((float)adc->adc0->analogRead(CH4));

    if (CH4_value < 10){
      st4 = "0000" + String (CH4_value);
    }
    else if (10< CH4_value && CH4_value <100){
      st4 = "000" + String (CH4_value);
    }
    else if (100 < CH4_value && CH4_value < 1000){
      st4 = "00" + String (CH4_value);
    }
    else if (1000 < CH4_value && CH4_value < 10000){
      st4 = "0" + String (CH4_value);
    }
    else {
      st4 =  String (CH4_value);
    }
  #endif

  #ifndef CHANNEL1
    st1 = "00000";
  #endif
  #ifndef CHANNEL2
    st2 = "00000";
  #endif
  #ifndef CHANNEL3
    st3 = "00000";
  #endif
  #ifndef CHANNEL4
    st4 = "00000";
  #endif

  String SendData = ini + st1 +  st2 + st3 + st4 + "\n";
  Serial.print (SendData);
  SendData.toCharArray (sendMe, 32);
  // Send message to receiver
  radio.writeFast(&sendMe, sizeof(sendMe));
}
