# MXEN4000/4004 Final Year Project
**Project Title:** Human-Machine interface through EMG sensors biofeedback and its application in rehabilitation or assistive systems  
**Project Subtitle:** Gesture Classification Using EMG Sensors and Machine Learning  
**Supervisor:** Prof. Tele Tan  
**Developer:** Dominic Hanssen (20179320)  


## OFFLINE
### Arduino_Scripts
#### FeatureDataCollection
fdcTransmitter.ino: WORKING  
- Hardware: Teensy 3.2  
- Reads adc data and sends over RF to Receiver  

fdcReceiver.ino: WORKING  
- Hardware: Teensy 4.0  
- Reads data from Transmitter and performs feature extraction  
- Sends feature data to PC over serial  
- Features Extracted: Mean Absolute Value, Root Mean Square, Waveform Length, Zero Crossings, Willison Amplitude and the Hjorth time-domain features Activity, Mobility, and Complexity  

#### Tools\RawDataCollection
rdcTransmitter.ino: WORKING  
- Hardware: Teensy 3.2  
- Reads adc data and sends over RF to Receiver  

rdcReceiver.ino: WORKING  
- Hardware: Teensy 4.0  
- Reads data from Transmitter sends to PC over serial  

### Python_Scripts
main.py: WORKING  
- Main python file  
- Command line arguments used to specify processes to run  

FeatureCollection.py: WORKING  
- Read feature struct sent over serial from Teensy 4.0  
- Decode and save feature data into .h5 file structure  

Classification.py: IN DEVELOPMENT  
- Perform supervised machine learning  
- Classification Algorithms: Support Vector Machine, K-Means Cluster, Naive Bayes  

#### Tools
Visualisation.py: WORKING  
- Plot feature data distribution  

RawDataCollection.py: WORKING  
- Collect raw data for m repetitions of n gestures  
- Save to .xlsx file  
- Data used for threshold computation for online process  

### Data Record
- Directory containing the .h5 data files for each session, along with plots of their feature distributions  

### Classification Record
- Directory containging the confusion matrices and classification reports for the offline classification runs  


## ONLINE
### Arduino_Scripts
onTransmitter.ino: DEVELOPMENT  
- Hardware: Teensy 3.2  
- Reads adc data and sends over RF to Receiver  

onReceiver.ino: DEVELOPMENT  
- Hardware: Teensy 4.0  
- Detects start of possible gesture based on readings from Transmitter  
- Records data until end of gesture detected otherwise data is discarded and process restarted  
- Performs feature extraction on possible gesture data and sends to PC over serial  

### Python_Scripts
ClassificationPipe.py: PLANNED  
- Trains optimal classification model based on findings from offline process  
- Reads and decodes each feature struct sent from Receiver  
- Attempts to classify feature data as one of the possible gestures  

### Threshold_Computation
- Directory containing .xlsx files containing data from RawDataCollection.py script for use in computing the on/off thresholds for the online scripts  

## TOOLS
### EmgPlotter
nrf24_transmitter.ino: WORKING  
- Hardware: Teensy 3.2  
- Transmitter code for EMG_PLOTTER.exe  

nrf24_receiver.ino: WORKING  
- Hardware: Teensy 4.0  
- Receiver code for EMG_PLOTTER.exe  

EMG_PLOTTER.exe: WORKING  
- GUI Executable provided by Amir Shabazi for viewing the sEMG signals for all four channels  

## Viewing .h5 Files
Can use ViTables to view .h5 and .hdf5 file contents  
Install & Run vitables.exe  
