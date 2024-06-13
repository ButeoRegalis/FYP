# MXEN4000/4004 Final Year Project (2 Channel Process)
**Project Title:** Human-Machine interface through EMG sensors biofeedback and its application in rehabilitation or assistive systems  
**Project Subtitle:** Gesture Classification Using EMG Sensors and Machine Learning  
**Supervisor:** Prof. Tele Tan  
**Developer:** Dominic Hanssen (20179320)  


## OFFLINE
### Arduino_Scripts
#### FeatureDataCollection
fdcTransmitter.ino: WORKING  
- Hardware: Teensy 3.2  
- Reads adc data for 2 sensor channels and sends over RF to Receiver  

fdcReceiver.ino: WORKING  
- Hardware: Teensy 4.0  
- Reads data from Transmitter and performs feature extraction on the data for each sensor channel  
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

Classification.py: WORKING  
- Perform supervised machine learning  
- Classification Algorithms: Support Vector Machine, K Nearest Neighbour, Complement Naive Bayes  

#### Tools
Visualisation.py: WORKING  
- Plot feature data distributions  

RawDataCollection.py: WORKING  
- Collect raw data for m repetitions of n gestures  
- Save to .xlsx file  
- Data used for threshold computation for online process  

### Data Record
- Directory containing the .h5 data files for each session, along with plots of their feature distributions  

### Classification Record
- Directory containging the confusion matrices and classification reports for the offline classification runs  


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
