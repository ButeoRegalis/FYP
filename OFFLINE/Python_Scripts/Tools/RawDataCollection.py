# RAW DATA COLLECTION FUNCTION
# STATUS: WORKING
# LAST UPDATED: 10/06/2024
# NOTE: Repeated use will result in file being overwritten


import serial
import struct
import numpy as np
import pandas as pd
from config import gesture_names


NUM_GESTURES = 5

startByte = b'\xff'
endByte = b'\xfe'
num_datapoints = 500
filename = 'Raw_Data.xlsx'


def collectRawData(port: str, baud: int, repetitions: int) -> None:
    """
    Read the feature data from the specified serial port, decode it and add it to the .h5 file.

    STATUS: WORKING

    : param port: serial comport to read from
    : type port: string
    : param baud: serial comport baudrate
    : type baud: integer
    : param h5file: .h5 file object
    : type h5file: File object
    : param repetitions: number of repetitions to record for each gesture
    : type repetitions: integer
    : return: table number
    : rtype: integer
    """

    try:
        # Define the serial connection
        print("Attempting to establish serial connection")
        link = serial.Serial(port=port, baudrate=baud, bytesize=serial.EIGHTBITS, timeout=None, parity=serial.PARITY_EVEN, rtscts=True)
        if link.is_open:
            link.close()
            link.open()
        serial_errors = 0

        if link:
            print("Serial connection established")
            print("Starting...")

            labels = []
            dataframes = []
            columns = []
            for ges in range(0, NUM_GESTURES, 1):
                print(f"Gesture: {gesture_names[ges]}")
                for rep in range(0, repetitions, 1):
                    print(f"Repetition: {rep}")
                    labels.append(gesture_names[ges])
                    datapoints = [[], []]
                    columns.append(['g' + str(object=ges) + '_r' + str(object=rep) + '_ch1', 'g' + str(object=ges) + '_r' + str(object=rep) + '_ch2'])
                    for data in range(0, num_datapoints, 1):
                        # Read data
                        serial_read = link.read(size=8)
                        # Decode data
                        data_struct = struct.unpack('ff', serial_read)
                        #print(data_struct)
                        # Add data to list
                        datapoints[0].append(data_struct[0])
                        datapoints[1].append(data_struct[1])
                    #print(datapoints)
                    dataframes.append(pd.DataFrame(data=datapoints, dtype=np.float16))
            #print(dataframes)
            dataframe = pd.concat(objs=dataframes, axis=1, ignore_index=True, names=columns)
            dataframe.to_excel(excel_writer=filename, sheet_name="Raw Data", float_format="%.4f", header=labels, index_label='index')

        print(f"Serial Errors: {serial_errors}")
        print("Data Collection Completed Successfully")
        print("EXITING...")
    except serial.SerialException as se:
        print("SERIAL EXCEPTION OCCURED IN RAW DATA COLLECTION PROCESS!\n")
        print(se)
    except:
        print("EXCEPTION OCCURED IN RAW DATA COLLECTION PROCESS!\n")
        import traceback
        traceback.print_exc()
    finally:
        link.close()
