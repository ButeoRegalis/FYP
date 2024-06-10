/*
 * Status: TESTABLE
 * Hardware: Teensy 3.2
 * Process: OFFLINE Feature Data Collection
 * Owner: Dominic Hanssen
 * Last updated: 10/06/2024
 */


/* Libraries */
#include <SPI.h>
#include <ADC.h>
#include <IntervalTimer.h>
#include <nRF24L01.h>
#include <RF24.h>


/* Global variables */
const uint8_t cePin = 9;
const uint8_t csnPin = 10;
const uint8_t piezoPin = 22;
const uint8_t readPin0 = A2;
const uint8_t readPin1 = A3;
const uint8_t readByte = 0x00;
const uint8_t startByte = 0xff;
const uint8_t offByte = 0x01;
const uint16_t buffer_size = 500;
const uint16_t tone_on = 200; // based off buffer_size + period0
const uint16_t tone_off = 300; // 1s between tones
const uint32_t period0 = 10000; // us (100 Hz, 5s for 500 datapoints)

const byte slaveAddress[] = {'R','x','A','A','A'};
const byte masterAddress[] = {'T','X','a','a','a'};

uint8_t startTimerValue0 = 0;
uint8_t msg = readByte;

volatile bool write_flag;
volatile uint16_t buffer_count = 0;


/* Global Objects */
ADC *adc = new ADC(); // adc object

IntervalTimer timer0; // timers

RF24 radio(cePin, csnPin); // Create a Radio

typedef struct {
  uint16_t adcVal0;
  uint16_t adcVal1;
} dataPacket;
dataPacket dPkt; // 2 channels (4 bytes)


/* Setup function. */
void setup()
{
  // PIEZO //
  pinMode(piezoPin, OUTPUT);

  // Serial //
  Serial.begin(115200);
  Serial.print("Initialising...");

  // Radio //
  bool rf = radio.begin();
  if (!rf)
  {
    radio.failureDetected = true;
    Serial.print("ERROR: RADIO FAILED TO INITIALISE!");
  }
  radio.setChannel(105);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  radio.setRetries(0,0);
  radio.setAutoAck(false);
  radio.stopListening();
  radio.openWritingPipe(slaveAddress);
  radio.openReadingPipe(1, masterAddress);
  radio.startListening();

  // ADC0 //
  pinMode(readPin0, INPUT_DISABLE);
  pinMode(readPin1, INPUT_DISABLE);
  adc->adc0->setAveraging(32);  // set number of averages
  adc->adc0->setResolution(16); // set bits of resolution
  adc->adc0->setConversionSpeed(ADC_CONVERSION_SPEED::MED_SPEED);
  adc->adc0->setSamplingSpeed(ADC_SAMPLING_SPEED::HIGH_SPEED);

  // Initialisation delay
  delay(500);
}


/* Loop function. */
void loop()
{
  while (msg == readByte)
  {
    if (radio.available())
    {
      Serial.println("Read...");
      radio.read(&msg, sizeof(msg));
    }
  }

  if (msg == startByte)
  {
    msg = offByte;
    write_flag = true;
    Serial.println("Writing...");
    radio.stopListening();
    startTimerValue0 = timer0.begin(timer0_callback, period0); // re/start timer
    delayMicroseconds(40);
    if (!startTimerValue0)
    {
      Serial.print("ERROR: TIMER DID NOT START!");
      tone(piezoPin, 1000, 10000);
    }
    else
    {
      Serial.println("Timer re/started");
    }
    adc->adc0->enableInterrupts(adc0_isr);
  }

  if (!write_flag)
  {
    timer0.end(); // stop timer
    Serial.println("Timer stopped");
    adc->adc0->disableInterrupts();
    radio.startListening();
    msg = readByte;
  }
}


/* Timer 0 callback function. */
void timer0_callback(void)
{
  adc->adc0->startSingleRead(readPin0);
  adc->adc0->startSingleRead(readPin1);

  if ((buffer_count == tone_on) || (buffer_count == tone_off))
  {
    Serial.println("Tone");
    tone(piezoPin, 2000, 100);
  }

  if (buffer_count < buffer_size)
  {
    Serial.println("RF Write");
    radio.writeFast(&dPkt, sizeof(dPkt));
    buffer_count++;
  }
  else if (buffer_count == buffer_size)
  {
    Serial.println("Reset");
    buffer_count = 0;
    write_flag = false;
  }
}


/* ADC0 interrupt call. */
void adc0_isr() {
  #if defined(__IMXRT1062__) // Teensy 4.0
    uint8_t pin = ADC::sc1a2channelADC0[ADC1_HC0 & 0x1f]; // the bits 0-4 of ADC0_SC1A have the channel
  #else
    uint8_t pin = ADC::sc1a2channelADC0[ADC0_SC1A & ADC_SC1A_CHANNELS]; // the bits 0-4 of ADC0_SC1A have the channel
  #endif

  if (pin == readPin0)
  {
    Serial.println("CH1 Read");
    dPkt.adcVal0 = (uint16_t)adc->adc0->readSingle();
  }
  else if (pin == readPin1)
  {
    Serial.println("CH2 Read");
    dPkt.adcVal1 = (uint16_t)adc->adc0->readSingle();
  }
  else // clear interrupt anyway
  {
    adc->readSingle();
  }

  // restore ADC config if it was in use before being interrupted by the analog timer
  if (adc->adc0->adcWasInUse)
  {
    // restore ADC config, and restart conversion
    adc->adc0->loadConfig(&adc->adc0->adc_config);
    // avoid a conversion started by this isr to repeat itself
    adc->adc0->adcWasInUse = false;
  }

  #if defined(__IMXRT1062__) // Teensy 4.0
    asm("DSB");
  #endif
}
