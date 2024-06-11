# FEATURE DATA DISTRIBUTION VISUALISATION FUNCTION
# STATUS: WORKING
# LAST UPDATED: 11/06/2024


import tables as tb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from config import NUM_GESTURES, NUM_CHANNELS, columns, gesture_names, gesture_indexes


def list_table_nums(h5file: tb.File) -> list:
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
        table_nums = []
    else:
        table_nums = sorted([int((x.split(" ")[0]).split("_")[-1]) for x in filtered_tables])

    return table_nums


def visualiseFeatureDistribution(hdfFile: str) -> None:
    try:
        # IMPORT DATA
        h5file = tb.open_file(filename=hdfFile, mode='r')
        tables = list_table_nums(h5file=h5file)
        dataframes = []
        for t in tables:
            table_name = "fset_" + str(object=t)
            nodeObject = h5file.get_node(where="/features", name=table_name)
            dataframes.append(pd.DataFrame.from_records(data=nodeObject.read(), columns=columns))  # type: ignore
        dataframe = pd.concat(objs=dataframes, axis=0, ignore_index=True)
        timestamp = dataframe['timestamp'].to_numpy(dtype=np.int64)
        labels = dataframe['label']
        dataframe = dataframe.drop(labels=['timestamp'], axis=1)

        # SORT DATA
        mav_list = []
        rms_list = []
        wl_list = []
        zc_list = []
        wa_list = []
        hj_a_list = []
        hj_m_list = []
        hj_c_list = []
        mav_avgs = []
        rms_avgs = []
        wl_avgs = []
        zc_avgs = []
        wa_avgs = []
        hj_a_avgs = []
        hj_m_avgs = []
        hj_c_avgs = []
        mav_yerrs = []
        rms_yerrs = []
        wl_yerrs = []
        zc_yerrs = []
        wa_yerrs = []
        hj_a_yerrs = []
        hj_m_yerrs = []
        hj_c_yerrs = []
        for l in range(0, len(gesture_names), 1):
            df = dataframe.loc[dataframe['label'] == l]
            # MAV
            ch0_mav = np.array(object=df['ch0_mav'], dtype=np.float16)
            ch1_mav = np.array(object=df['ch1_mav'], dtype=np.float16)
            mav_list.append([ch0_mav, ch1_mav])
            mav_avgs += [np.average(a=ch0_mav), np.average(a=ch1_mav)]
            # RMS
            ch0_rms = np.array(object=df['ch0_rms'], dtype=np.float16)
            ch1_rms = np.array(object=df['ch1_rms'], dtype=np.float16)
            rms_list.append([ch0_rms, ch1_rms])
            rms_avgs += [np.average(a=ch0_rms), np.average(a=ch1_rms)]
            # WL
            ch0_wl = np.array(object=df['ch0_wl'], dtype=np.float16)
            ch1_wl = np.array(object=df['ch1_wl'], dtype=np.float16)
            wl_list.append([ch0_wl, ch1_wl])
            wl_avgs += [np.average(a=ch0_wl), np.average(a=ch1_wl)]
            # ZC
            ch0_zc = np.array(object=df['ch0_zc'], dtype=np.float16)
            ch1_zc = np.array(object=df['ch1_zc'], dtype=np.float16)
            zc_list.append([ch0_zc, ch1_zc])
            zc_avgs += [np.average(a=ch0_zc), np.average(a=ch1_zc)]
            # WA
            ch0_wa = np.array(object=df['ch0_wa'], dtype=np.float16)
            ch1_wa = np.array(object=df['ch1_wa'], dtype=np.float16)
            wa_list.append([ch0_wa, ch1_wa])
            wa_avgs += [np.average(a=ch0_wa), np.average(a=ch1_wa)]
            # HJ_A
            ch0_hj_a = np.array(object=df['ch0_hj_a'], dtype=np.float16)
            ch1_hj_a = np.array(object=df['ch1_hj_a'], dtype=np.float16)
            hj_a_list.append([ch0_hj_a, ch1_hj_a])
            hj_a_avgs += [np.average(a=ch0_hj_a), np.average(a=ch1_hj_a)]
            # HJ_M
            ch0_hj_m = np.array(object=df['ch0_hj_m'], dtype=np.float16)
            ch1_hj_m = np.array(object=df['ch1_hj_m'], dtype=np.float16)
            hj_m_list.append([ch0_hj_m, ch0_hj_m])
            hj_m_avgs += [np.average(a=ch0_hj_m), np.average(a=ch1_hj_m)]
            # HJ_C
            ch0_hj_c = np.array(object=df['ch0_hj_c'], dtype=np.float16)
            ch1_hj_c = np.array(object=df['ch1_hj_c'], dtype=np.float16)
            hj_c_list.append([ch0_hj_c, ch1_hj_c])
            hj_c_avgs += [np.average(a=ch0_hj_c), np.average(a=ch1_hj_c)]
        i = 0
        for g in range(0, NUM_GESTURES, 1):
            for c in range(0, NUM_CHANNELS, 1):
                i += c
                mav_yerrs.append([abs(mav_avgs[i] - np.amin(a=mav_list[g][0])), abs(mav_avgs[i] - np.amax(a=mav_list[g][1]))])
                rms_yerrs.append([abs(rms_avgs[i] - np.amin(a=rms_list[g][0])), abs(rms_avgs[i] - np.amax(a=rms_list[g][1]))])
                wl_yerrs.append([abs(wl_avgs[i] - np.amin(a=wl_list[g][0])), abs(wl_avgs[i] - np.amax(a=wl_list[g][1]))])
                zc_yerrs.append([abs(zc_avgs[i] - np.amin(a=zc_list[g][0])), abs(zc_avgs[i] - np.amax(a=zc_list[g][1]))])
                wa_yerrs.append([abs(wa_avgs[i] - np.amin(a=wa_list[g][0])), abs(wa_avgs[i] - np.amax(a=wa_list[g][1]))])
                hj_a_yerrs.append([abs(hj_a_avgs[i] - np.amin(a=hj_a_list[g][0])), abs(hj_a_avgs[i] - np.amax(a=hj_a_list[g][1]))])
                hj_m_yerrs.append([abs(hj_m_avgs[i] - np.amin(a=hj_m_list[g][0])), abs(hj_m_avgs[i] - np.amax(a=hj_m_list[g][1]))])
                hj_c_yerrs.append([abs(hj_c_avgs[i] - np.amin(a=hj_c_list[g][0])), abs(hj_c_avgs[i] - np.amax(a=hj_c_list[g][1]))])
        labels = np.repeat(a=np.arange(start=0, stop=5, step=1), repeats=2)
        print(f"Labels: {labels}")

        # PLOT DATA
        colours = ['red', 'orange', 'yellowgreen', 'deepskyblue', 'darkorchid']
        pad = 1.0
        figsize = (8, 10)
        plt.figure(num=1, figsize=figsize)
        plt.subplot(4, 1, 1)
        plt.tight_layout(pad=pad)
        plt.errorbar(x=labels, y=mav_avgs, yerr=mav_yerrs, fmt='none', ecolor='darkgray')
        plt.scatter(x=labels, y=mav_avgs, c=colours)
        plt.xticks(ticks=gesture_indexes, labels=gesture_names)
        plt.ylim(0, 3.3)
        plt.yticks(ticks=np.arange(start=0, stop=3.6, step=0.3))
        plt.title(label='MAV')

        plt.subplot(4, 1, 2)
        plt.tight_layout(pad=pad)
        plt.errorbar(x=labels, y=rms_avgs, yerr=rms_yerrs, fmt='none', ecolor='darkgray')
        plt.scatter(x=labels, y=rms_avgs, c=colours)
        plt.xticks(ticks=gesture_indexes, labels=gesture_names)
        plt.ylim(0, 3.3)
        plt.yticks(ticks=np.arange(start=0, stop=3.6, step=0.3))
        plt.title(label='RMS')

        plt.subplot(4, 1, 3)
        plt.tight_layout(pad=pad)
        plt.errorbar(x=labels, y=wl_avgs, yerr=wl_yerrs, fmt='none', ecolor='darkgray')
        plt.scatter(x=labels, y=wl_avgs, c=colours)
        plt.xticks(ticks=gesture_indexes, labels=gesture_names)
        plt.ylim(0, 3.3)
        plt.yticks(ticks=np.arange(start=0, stop=3.6, step=0.3))
        plt.title(label='WL')

        plt.subplot(4, 1, 4)
        plt.tight_layout(pad=pad)
        plt.errorbar(x=labels, y=zc_avgs, yerr=zc_yerrs, fmt='none', ecolor='darkgray')
        plt.scatter(x=labels, y=zc_avgs, c=colours)
        plt.xticks(ticks=gesture_indexes, labels=gesture_names)
        plt.ylim(bottom=0)
        plt.title(label='ZC')
        plt.show()

        plt.figure(num=2, figsize=figsize)
        plt.subplot(4, 1, 1)
        plt.tight_layout(pad=pad)
        plt.errorbar(x=labels, y=wa_avgs, yerr=wa_yerrs, fmt='none', ecolor='darkgray')
        plt.scatter(x=labels, y=wa_avgs, c=colours)
        plt.xticks(ticks=gesture_indexes, labels=gesture_names)
        plt.ylim(bottom=0)
        plt.title(label='WA')

        plt.subplot(4, 1, 2)
        plt.tight_layout(pad=pad)
        plt.errorbar(x=labels, y=hj_a_avgs, yerr=hj_a_yerrs, fmt='none', ecolor='darkgray')
        plt.scatter(x=labels, y=hj_a_avgs, c=colours)
        plt.xticks(ticks=gesture_indexes, labels=gesture_names)
        plt.ylim(bottom=0)
        plt.title(label='HJ_A')

        plt.subplot(4, 1, 3)
        plt.tight_layout(pad=pad)
        plt.errorbar(x=labels, y=hj_m_avgs, yerr=hj_m_yerrs, fmt='none', ecolor='darkgray')
        plt.scatter(x=labels, y=hj_m_avgs, c=colours)
        plt.xticks(ticks=gesture_indexes, labels=gesture_names)
        plt.ylim(bottom=0)
        plt.title(label='HJ_M')

        plt.subplot(4, 1, 4)
        plt.tight_layout(pad=pad)
        plt.errorbar(x=labels, y=hj_c_avgs, yerr=hj_c_yerrs, fmt='none', ecolor='darkgray')
        plt.scatter(x=labels, y=hj_c_avgs, c=colours)
        plt.xticks(ticks=gesture_indexes, labels=gesture_names)
        plt.ylim(bottom=0)
        plt.title(label='HJ_C')
        plt.show()

        plt.show()
        print("DONE.")
    except:
        print("EXCEPTION OCCURED IN VISUALISATION PROCESS!\n")
        import traceback
        traceback.print_exc()
    finally:
        h5file.close()
