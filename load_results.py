
from utils.utils import update_data, get_video, get_audio, get_frames, build_test_dataset, transport_ds, prepare_clip_zero_shoot
from os.path import join, exists
import os
import numpy as np
import csv
import pickle
from PIL import Image

mini_set_path = '../results/zero_shoot.pickle'
if exists(mini_set_path):
    with open(mini_set_path, 'rb') as handle:
        [clip_tuple, classes, test_values, test_indices] = pickle.load(handle)

classes = np.array(classes)
in_top5 = 0
in_top3 = 0
in_top1 = 0
for tuple, values, indices in zip(clip_tuple, test_values, test_indices):
    class_id = tuple[1]
    if class_id in classes[indices[0]]:
        in_top5 = in_top5 +1
        in_top3 = in_top3 +1
        in_top1 = in_top1 +1
    elif class_id in classes[indices[0:3]]:
        in_top5 = in_top5 +1            
        in_top3 = in_top3 +1
    elif class_id in classes[indices[0:5]]:
        in_top5 = in_top5 +1  
    
    print("\nTop predictions for",class_id,":\n")
    for value, index in zip(values, indices):
        print(classes[index]+':', "{:.2%}".format(value))

print('\n\nRESULTS:\n')

print(in_top1,'/',len(clip_tuple), 'found in top1 from CLIP.',"{:.2%}".format(in_top1/len(clip_tuple)))
print(in_top3,'/',len(clip_tuple), 'found in top3 from CLIP.',"{:.2%}".format(in_top3/len(clip_tuple)))
print(in_top5,'/',len(clip_tuple), 'found in top5 from CLIP.',"{:.2%}".format(in_top5/len(clip_tuple)))
