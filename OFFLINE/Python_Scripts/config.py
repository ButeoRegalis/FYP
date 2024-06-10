# CONFIG FILE
# LAST UPDATED: 10/06/2024

NUM_CHANNELS = 2
NUM_GESTURES = 5

columns = [('timestamp', 'u8'), ('label', 'u2'),
           ('ch1_mav', 'f2'), ('ch2_mav', 'f2'),
           ('ch1_rms', 'f2'), ('ch2_rms', 'f2'),
           ('ch1_wl', 'f2'), ('ch2_wl', 'f2'),
           ('ch1_zc', 'f2'), ('ch2_zc', 'f2'),
           ('ch1_wa', 'f2'), ('ch2_wa', 'f2'),
           ('ch1_hj_a', 'f2'), ('ch2_hj_a', 'f2'),
           ('ch1_hj_m', 'f2'), ('ch2_hj_m', 'f2'),
           ('ch1_hj_c', 'f2'), ('ch2_hj_c', 'f2')]

feature_names = ['ch1_mav', 'ch2_mav',
                 'ch1_rms', 'ch2_rms',
                 'ch1_wl', 'ch2_wl',
                 'ch1_zc', 'ch2_zc',
                 'ch1_wa', 'ch2_wa',
                 'ch1_hj_a', 'ch2_hj_a',
                 'ch1_hj_m', 'ch2_hj_m',
                 'ch1_hj_c', 'ch2_hj_c']

gesture_names = ['asl for 1', 'asl for 2', 'asl for 3', 'asl for 4', 'asl for 5']

gesture_indexes = [0, 1, 2, 3, 4]
