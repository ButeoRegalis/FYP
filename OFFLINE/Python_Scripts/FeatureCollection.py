# FEATURE DATA COLLECTION FUNCTION
# STATUS: WORKING
# LAST UPDATED: 10/06/2024
# NOTE: ~0.2s for read + write


import os
import serial
import struct
import tables as tb
import numpy as np
import time as tm
import datetime as dt
from config import NUM_CHANNELS, NUM_GESTURES


startByte = b'\xff'
endByte = b'\xfe'
gesture_map = {0: 'asl for 1', 1: 'asl for 2', 2: 'asl for 3', 3: 'asl for 4', 4: 'asl for 5'}


class featureData(tb.IsDescription):
    timestamp = tb.UInt64Col()
    label = tb.UInt8Col()  # Gesture label
    ch1_mav = tb.Float32Col()  # Mean Absolute Value
    ch2_mav = tb.Float32Col()
    ch1_rms = tb.Float32Col()  # Root Mean Square
    ch2_rms = tb.Float32Col()
    ch1_wl = tb.Float32Col()  # Waveform Length
    ch2_wl = tb.Float32Col()
    ch1_zc = tb.Float32Col()  # Zero Crossings
    ch2_zc = tb.Float32Col()
    ch1_wa = tb.Float32Col()  # Willizon Amplitude
    ch2_wa = tb.Float32Col()
    ch1_hj_a = tb.Float32Col()  # Hjorth time-domain feature: Activity
    ch2_hj_a = tb.Float32Col()
    ch1_hj_m = tb.Float32Col()  # Hjorth time-domain feature: Mobility
    ch2_hj_m = tb.Float32Col()
    ch1_hj_c = tb.Float32Col()  # Hjorth time-domain feature: Complexity
    ch2_hj_c = tb.Float32Col()


def get_set_num(h5file: tb.File) -> int:
    """
    Get new table number based on existing tables in features group of .h5 file

    STATUS: WORKING

    : param h5file: .h5 file object
    : type h5file: File object
    : return: table number
    : rtype: integer
    """

    nodes = []
    for node in h5file:
        nodes.append(str(object=node))

    filtered_tables = list(filter(lambda x: '(Table' in x, nodes))
    if not filtered_tables:  # no groups found
        table_num = 0
    else:
        table_nums = [int((x.split(" ")[0]).split("_")[-1]) for x in filtered_tables]
        table_num = max(table_nums) + 1

    return table_num


def collectFeatureData(port: str, baud: int, hdfFile: str, repetitions: int) -> None:
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

    if os.path.exists(path=hdfFile):
        print("Attempting to open file")
        try:
            h5file = tb.open_file(filename=hdfFile, mode='r+')
            print("File opened")
        except:
            print("PYTABLES EXCEPTION OCCURRED!")
            print(f"IF HDF5ExtError: Most likely cause is {hdfFile} is empty")
            print("If this is the case delete the file and restart the script")
            print("EXITING...")
            exit(code=1)
    else:
        print(f"Existing file not found. Creating new file {hdfFile}")
        h5file = tb.open_file(filename=hdfFile, mode='w')
        group = h5file.create_group(where="/", name="features")  # create new group
        group._v_attrs.creation = dt.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")  # add date group created to metadata
        print("New file created")

    try:
        # Define .h5 file structure
        table_num = get_set_num(h5file=h5file)
        table_name = "fset_" + str(object=table_num)
        print(f"Table: {table_name}")
        session_time = dt.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        featureTable = h5file.create_table(where="/features", name=table_name, description=featureData, title=f"Feature data for session {session_time}")  # new table created for each gesture
        data = featureTable.row

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

            for ges in range(0, NUM_GESTURES, 1):
                print(f"Gesture: {gesture_map[ges]}")

                for rep in range(0, repetitions, 1):
                    print(f"Repetition: {rep}")
                    print(f"Start = {tm.time_ns()} ns")

                    for cha in range(0, NUM_CHANNELS, 1):
                        print(f"Channel: {cha}")

                        # Read & decode data
                        serial_read = link.read(size=30)
                        print(serial_read.hex(sep=':'))
                        feature_struct = struct.unpack('=HfffHHfff', serial_read)
                        print(feature_struct)

                        # Add data to buffer
                        if cha == 0:
                            data['timestamp'] = np.uint64(tm.time_ns())
                            data['label'] = ges
                        data['ch' + str(object=cha) + '_mav'] = feature_struct[1]
                        data['ch' + str(object=cha) + '_rms'] = feature_struct[2]
                        data['ch' + str(object=cha) + '_wl'] = feature_struct[3]
                        data['ch' + str(object=cha) + '_zc'] = feature_struct[4]
                        data['ch' + str(object=cha) + '_wa'] = feature_struct[5]
                        data['ch' + str(object=cha) + '_hj_a'] = feature_struct[6]
                        data['ch' + str(object=cha) + '_hj_m'] = feature_struct[7]
                        data['ch' + str(object=cha) + '_hj_c'] = feature_struct[8]
                        if cha == 1:
                            data.append()

                    print(f"End = {tm.time_ns()} ns")

                # Write data to file
                featureTable.flush()

        print(f"Serial Errors: {serial_errors}")
        print("Data Collection Completed Successfully")
        print("EXITING...")
    except serial.SerialException as se:
        print("SERIAL EXCEPTION OCCURED IN DATA COLLECTION PROCESS!\n")
        print(se)
    except:
        print("EXCEPTION OCCURED IN DATA COLLECTION PROCESS!\n")
        import traceback
        traceback.print_exc()
    finally:
        link.close()
        h5file.close()
