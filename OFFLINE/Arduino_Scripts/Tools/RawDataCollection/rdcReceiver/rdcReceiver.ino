/*
 * Status: WORKING
 * Hardware: Teensy 4.0
 * Process: OFFLINE Raw Data Collection
 * Owner: Dominic Hanssen
 * Last updated: 10/06/2024
 *
 * NOTE 1: DEBUG must be disabled for normal operation
 */


/* Libraries */
#include <SPI.h>
#include <ADC.h>
#include <IntervalTimer.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <cmath>


/* Global variables */
// define DEBUG to enable debugging on serial
//#define DEBUG
const uint8_t cePin = 9;
const uint8_t csnPin = 10;
const uint8_t ledPin = LED_BUILTIN;
const uint8_t startByte = 0xff; // IMPORTANT: must match that in transmitter.ino
const uint8_t adcRes = 16; // IMPORTANT: must match that in transmitter.ino
const uint16_t buffer_raw_size = 500; // IMPORTANT: must match that in transmitter.ino
const uint32_t period0 = 10000; // us (100 Hz, 5s for 500 datapoints)

const double sysVol = 3.3; // Teensy 4.0 system voltage [V]

const byte slaveAddress[] = {'R','x','A','A','A'};
const byte masterAddress[] = {'T','X','a','a','a'};

uint8_t startTimerValue0 = 0;

double ch1_buffer_raw[buffer_raw_size] = {0};
double ch2_buffer_raw[buffer_raw_size] = {0};

volatile bool write_flag = false;
volatile uint16_t buffer_count = 0;


/* Global Objects */
ADC *adc = new ADC(); // adc object

IntervalTimer timer0; // timers

RF24 radio(cePin, csnPin); // Create a Radio

typedef struct {
  uint16_t adcVal0; // 2 bytes
  uint16_t adcVal1; // 2 bytes
} adcValDataPacket;
adcValDataPacket adcPkt; // Total = 4 bytes (2 channels)

typedef struct {
  float ch1_data; // 4 bytes
  float ch2_data; // 4 bytes
} dataPacket;
dataPacket dPkt; // Total = 8 bytes


/* Setup function. */
void setup()
{
  // LED //
  pinMode(ledPin, OUTPUT);
  digitalWriteFast(ledPin, LOW);

  // Serial //
  Serial.begin(115200); // ignored

  // Radio //
  bool rf = radio.begin();
  if (!rf) // RADIO FAILED TO INITIALISE
  {
    #ifdef DEBUG
      Serial.println("RADIO FAILED TO INITIALISE");
      Serial.flush();
    #endif
    radio.failureDetected = true;
    digitalWriteFast(ledPin, HIGH);
  }
  radio.setChannel(105);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  radio.setRetries(0,0);
  radio.setAutoAck(false);
  radio.stopListening();
  radio.openWritingPipe(masterAddress);
  radio.openReadingPipe(1, slaveAddress);
  delay(10000); // python script start delay
  radio.write(&startByte, sizeof(int));
  radio.startListening();

  // Timer 0 //
  startTimerValue0 = timer0.begin(timer0_callback, period0);
  delay(500); // timer initialisation delay
}


/* Loop function. */
void loop()
{
  if (!startTimerValue0) // TIMER0 FAILED TO INITIALISE
  {
    #ifdef DEBUG
      Serial.println("TIMER0 FAILED TO INITIALISE");
      Serial.flush();
    #endif
    digitalWriteFast(ledPin, HIGH);
  }

  if (write_flag)
  {
    write_flag = false;

    send();
    for (int i = 0; i < buffer_raw_size; i++) // reset buffers to all 0
    {
      ch1_buffer_raw[i] = 0.0;
      ch2_buffer_raw[i] = 0.0;
    }
    startTimerValue0 = timer0.begin(timer0_callback, period0); // restart timer

    radio.stopListening();
    radio.write(&startByte, sizeof(int));
    radio.startListening();
  }
}


/* Data transmission function. */
void send(void)
{
  #ifdef DEBUG
    uint32_t start = micros();
  #endif

  for (int i = 0; i < buffer_raw_size; i++)
  {
    // Add data to struct
    dPkt.ch1_data = (float)ch1_buffer_raw[i];
    dPkt.ch2_data = (float)ch2_buffer_raw[i];
    #ifdef DEBUG
      Serial.println(dPkt.data);
    #endif

    // Write data to serial buffer
    Serial.write((const byte *)&dPkt, sizeof(dPkt));
    delayMicroseconds(100);
  }

  // Delay
  #ifdef DEBUG
    uint32_t end = micros();
    Serial.print("Send function duration: ");
    Serial.println(end - start);
  #endif
  delay(5000); // python script read delay
}


/* Timer 0 callback function. */
void timer0_callback(void)
{
  if (buffer_count == buffer_raw_size - 1) // stop timer as soon as possible
  {
    timer0.end();
  }

  if (radio.available())
  {
    if (buffer_count < buffer_raw_size)
    {
      radio.read(&adcPkt, sizeof(adcPkt));
      ch1_buffer_raw[buffer_count + 1] = (double)(adcPkt.adcVal0*(sysVol/pow(2, adcRes)));
      ch2_buffer_raw[buffer_count + 1] = (double)(adcPkt.adcVal1*(sysVol/pow(2, adcRes)));
      buffer_count++;
    }
  }
  if (buffer_count == buffer_raw_size)
  {
    buffer_count = 0;
    write_flag = true;
  }
}
