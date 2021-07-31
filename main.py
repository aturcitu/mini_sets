
from utils.utils import update_data, get_video, get_audio, get_frames, build_test_dataset
from os.path import join, exists

import numpy as np
import pickle
import csv

csv_path = './data'

classes = []
data = {}

# Read classes on DS
with open(join(csv_path, 'stat.csv')) as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        classes.append(row[0])

# Read DS info
with open(join(csv_path, 'vggsound.csv'))as f:
    csv_reader = csv.reader(f)
    for item in csv_reader:
        if item[2] in classes:
            data = update_data(data, *item)

# Create a miniDS with n sampels per class
samples_class = 25
mini_set_path = '../../datasets/mini_sounds_'+str(samples_class)+'.pickle'
if exists(mini_set_path):
    with open(mini_set_path, 'rb') as handle:
        mini_data = pickle.load(handle)
else:
    black_list = {}
    to_remove = [0]
    while(len(to_remove)):
        mini_data = build_test_dataset(data, black_list, samples_class)
        mini_data, to_remove = get_video(mini_data)
        black_list.update(to_remove)
    with open(mini_set_path, 'wb') as handle:
        pickle.dump(mini_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # extrac audio from videos
    get_audio(mini_data)
    get_frames(mini_data)

print('done')
