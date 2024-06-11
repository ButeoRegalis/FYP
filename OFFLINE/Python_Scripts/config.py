# CONFIG FILE
# LAST UPDATED: 11/06/2024


NUM_CHANNELS = 2
NUM_GESTURES = 5
BUFFER_RAW_SIZE = 500

columns = [('timestamp', 'u8'), ('label', 'u2'),
           ('ch0_mav', 'f2'), ('ch1_mav', 'f2'),
           ('ch0_rms', 'f2'), ('ch1_rms', 'f2'),
           ('ch0_wl', 'f2'), ('ch1_wl', 'f2'),
           ('ch0_zc', 'f2'), ('ch1_zc', 'f2'),
           ('ch0_wa', 'f2'), ('ch1_wa', 'f2'),
           ('ch0_hj_a', 'f2'), ('ch1_hj_a', 'f2'),
           ('ch0_hj_m', 'f2'), ('ch1_hj_m', 'f2'),
           ('ch0_hj_c', 'f2'), ('ch1_hj_c', 'f2')]

feature_names = ['ch0_mav', 'ch1_mav',
                 'ch0_rms', 'ch1_rms',
                 'ch0_wl', 'ch1_wl',
                 'ch0_zc', 'ch1_zc',
                 'ch0_wa', 'ch1_wa',
                 'ch0_hj_a', 'ch1_hj_a',
                 'ch0_hj_m', 'ch1_hj_m',
                 'ch0_hj_c', 'ch1_hj_c']

gesture_names = ['asl for 1', 'asl for 2', 'asl for 3', 'asl for 4', 'asl for 5']

gesture_indexes = [0, 1, 2, 3, 4]
