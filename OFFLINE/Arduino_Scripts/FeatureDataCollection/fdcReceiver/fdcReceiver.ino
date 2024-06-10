/*
 * Status: TESTABLE
 * Hardware: Teensy 4.0
 * Process: OFFLINE Feature Data Collection
 * Owner: Dominic Hanssen
 * Last updated: 10/06/2024
 *
 * extract() function duration: 113 us
 * feature data transmission rate: every 5.025 s (does not include delays)
 *
 * NOTE 1: DEBUG must be disabled for normal operation
 * NOTE 2: enable SMOOTH to perform smoothing of data before feature extraction
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
// define SMOOTH to perform smoothing on data before feature extraction. Note smoothing reduces buffer size to buffer_raw_size - window + 1
#define SMOOTH
const uint8_t cePin = 9;
const uint8_t csnPin = 10;
const uint8_t ledPin = LED_BUILTIN;
const uint8_t startByte = 0xff; // IMPORTANT: must match that in transmitter.ino
const uint8_t adcRes = 16; // IMPORTANT: must match that in transmitter.ino
const uint8_t num_channels = 2;
const uint16_t window = 20; // Moving Average Algorithm window length
const uint16_t buffer_raw_size = 500; // IMPORTANT: must match that in transmitter.ino
const uint16_t tone_on = 200; // IMPORTANT: must match that in transmitter.ino
const uint16_t tone_off = 300; // IMPORTANT: must match that in transmitter.ino
const uint16_t start_cut_error = 25;
const uint16_t end_cut_error = 50;
const uint16_t buffer_cut_size = start_cut_error + (tone_off - tone_on) + end_cut_error; // must be smaller than buffer_raw_size - window
const uint32_t period0 = 10000; // us (100 Hz, 5s for 500 datapoints)

const double sysVol = 3.3; // Teensy 4.0 system voltage [V]
const double zeroOffset = 1.65; // Zero Crossings zero offset [V]
const double willisonThreshold = 0.01; // Willison Amplitude threshold [V]

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
} dataPacket;
dataPacket dPkt; // Total = 4 bytes (2 channels)

typedef struct {
  uint16_t channel; // 2 bytes
  float mav; // 4 bytes
  float rms; // 4 bytes
  float wl; // 4 bytes
  uint16_t zc; // 2 bytes
  uint16_t wa; // 2 bytes
  float hj_a; // 4 bytes
  float hj_m; // 4 bytes
  float hj_c; // 4 bytes
} featurePacket; // Total = 30 bytes
featurePacket fPkt;


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

    #ifdef DEBUG
      uint32_t start = micros();
    #endif
    extract(ch1_buffer_raw, 1);
    extract(ch2_buffer_raw, 2);
    #ifdef DEBUG
      uint32_t end = micros();
      Serial.print("Total Extraction Duration: ");
      Serial.println(end-start);
    #endif

    for (int i = 0; i < buffer_raw_size; i++) // reset buffers to all 0
    {
      ch1_buffer_raw[i] = 0.0;
      ch2_buffer_raw[i] = 0.0;
    }
    startTimerValue0 = timer0.begin(timer0_callback, period0); // restart timer

    #ifdef DEBUG
      Serial.println("Entering Read Mode.");
    #endif
    radio.stopListening();
    radio.write(&startByte, sizeof(int));
    radio.startListening();
  }
}


/* Feature extraction function. */
void extract(double *data, uint16_t channel_num)
{
  #ifdef DEBUG
    Serial.print("Starting Feature Extraction on Channel ");
    Serial.println(channel_num);
    uint32_t start = micros();
  #endif

  uint16_t buffer_size = buffer_raw_size; // Define buffer_size
  #ifdef SMOOTH
    // Smoothing
    // Uses Moving Average Algorithm
    double buffer_smooth[buffer_size] = {0};

    for (int i = 0; i < buffer_size - window; i++)
    {
      // Calculate mean of slice
      double mean = 0;
      for (int j = 0; j < window; j++)
      {
        mean += *(data + i + j);
      }
      mean /= window;
      // Add mean to buffer_smooth
      buffer_smooth[i] = mean;
    }

    data = buffer_smooth; // Point data to smoothed data buffer
    buffer_size = buffer_raw_size - window; // Update buffer_size
  #endif

  #ifdef DEBUG
    Serial.print("[");
    for (int i = 0; i < buffer_size; i++)
    {
      
      Serial.print(*(data + i));
      Serial.print(", ");
    }
    Serial.println("]");
  #endif

  // Data Reduction
  // Reduce to range of data in which gesture was performed
  double buffer_cut[buffer_cut_size] = {0};
  for (int i = 0; i < buffer_cut_size; i++)
  {
    buffer_cut[i] = *(data + (tone_on - start_cut_error) + i);
  }
  data = buffer_cut; // Point data to smoothed data buffer
  buffer_size = buffer_cut_size; // Update buffer_size

  #ifdef DEBUG
    Serial.print("Buffer size: ");
    Serial.println(buffer_size);
  #endif

  // Mean Absolute Value (MAV)
  double mean_absolute_value = 0;
  for (int i = 0; i < buffer_size; i++)
  {
    mean_absolute_value += *(data + i);
  }
  mean_absolute_value /= buffer_size;

  // Root Mean Square (RMS)
  double squared_mean = 0;
  for (int i = 0; i < buffer_size; i++)
  {
    squared_mean += pow(*(data + i), 2);
  }
  double root_mean_square = sqrt(squared_mean / buffer_size);

  // Waveform Length (WL)
  double waveform_length = 0;
  for (int i = 0; i < buffer_size - 1; i++)
  {
    waveform_length += (double)abs(*(data + i + 1) - *(data + i));
  }

  // Zero Crossings (ZC)
  uint16_t zero_crossings = 0;
  for (int i = 0; i < buffer_size - 1; i++)
  {
    if ((*(data + i) >= zeroOffset) && (*(data + i + 1) < zeroOffset))
    {
      zero_crossings++;
    }
    if ((*(data + i) < zeroOffset) && (*(data + i + 1) >= zeroOffset))
    {
      zero_crossings++;
    }
  }

  // Willison Amplitude (WA)
  uint16_t willison_amplitude = 0;
  for (int i = 0; i < buffer_size - 1; i++)
  {
    if (abs((*(data + i) - *(data + i + 1))) >= willisonThreshold)
    {
      willison_amplitude++;
    }
  }

  // Hjorth Time-Domain Features (HJ)
  // Reference: https://intapi.sciendo.com/pdf/10.2478/joeb-2023-0009
  // Differential computation based off numpy.diff method
  // Activity (HJ_A)
  double var_zero = 0;
  for (int i = 0; i < buffer_size; i++)
  {
    var_zero += pow(*(data + i) - mean_absolute_value, 2);
  }
  var_zero /= buffer_size; // variance
  double activity = var_zero;

  // Mobility (HJ_M)
  double df_one[buffer_size] = {0};
  for (int i = 0; i < buffer_size - 1; i++)
  {
    df_one[i] = *(data + i + 1) - *(data + i);
  }
  double mav_one = 0;
  for (int i = 0; i < buffer_size; i++)
  {
    mav_one += *(df_one + i);
  }
  mav_one /= buffer_size;
  double var_one = 0;
  for (int i = 0; i < buffer_size; i++)
  {
    var_one += pow(*(df_one + i) - mav_one, 2);
  }
  var_one /= (buffer_size - 1);
  double mobility = sqrt(var_one/var_zero);

  // Complexity (HJ_C)
  double df_two[buffer_size] = {0};
  for (int i = 0; i < buffer_size - 1; i++)
  {
    df_two[i] = *(df_one + i + 1) - *(df_one + i);
  }
  double mav_two = 0;
  for (int i = 0; i < buffer_size; i++)
  {
    mav_two += *(df_two + i);
  }
  mav_two /= buffer_size;
  double var_two = 0;
  for (int i = 0; i < buffer_size; i++)
  {
    var_two += pow(*(df_two + i) - mav_two, 2);
  }
  var_two /= (buffer_size - 1);
  double complexity = sqrt(var_two/var_one)/mobility;

  // Add features to struct
  fPkt.channel = channel_num;
  fPkt.mav = (float)mean_absolute_value;
  fPkt.rms = (float)root_mean_square;
  fPkt.wl = (float)waveform_length;
  fPkt.zc = zero_crossings;
  fPkt.wa = willison_amplitude;
  fPkt.hj_a = (float)activity;
  fPkt.hj_m = (float)mobility;
  fPkt.hj_c = (float)complexity;
  #ifdef DEBUG
    Serial.print("Feature Struct {");
    Serial.print(fPkt.channel);
    Serial.print(", ");
    Serial.print(fPkt.mav);
    Serial.print(", ");
    Serial.print(fPkt.rms);
    Serial.print(", ");
    Serial.print(fPkt.wl);
    Serial.print(", ");
    Serial.print(fPkt.zc);
    Serial.print(", ");
    Serial.print(fPkt.wa);
    Serial.print(", ");
    Serial.print(fPkt.hj_a);
    Serial.print(", ");
    Serial.print(fPkt.hj_m);
    Serial.print(", ");
    Serial.print(fPkt.hj_c);
    Serial.println("}");
    Serial.flush();
  #endif

  // Write data to serial buffer
  Serial.write((const byte*)&fPkt, sizeof(fPkt));

  // Delay
  #ifdef DEBUG
    uint32_t end = micros();
    Serial.print("Channel ");
    Serial.println(channel_num);
    Serial.print(" Extraction Duration: ");
    Serial.println(end-start);
  #endif
  delay(350); // python script read delay
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
      radio.read(&dPkt, sizeof(dPkt));
      ch1_buffer_raw[buffer_count + 1] = (double)(dPkt.adcVal0 * (sysVol / pow(2, adcRes)));
      ch2_buffer_raw[buffer_count + 1] = (double)(dPkt.adcVal1 * (sysVol / pow(2, adcRes)));
      buffer_count++;
    }
  }
  if (buffer_count == buffer_raw_size)
  {
    buffer_count = 0;
    write_flag = true;
    #ifdef DEBUG
      Serial.println("Entering Write Mode.");
    #endif
  }
}
