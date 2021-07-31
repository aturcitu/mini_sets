
from utils.utils import update_data, get_video, get_audio, get_frames, build_test_dataset
from os.path import join, exists

import numpy as np
import argparse
import pickle
import csv


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data_path',
        default='./data',
        type=str,
        help='Directory path of CVS data')    
    parser.add_argument(
        '--ds_path',
        default='../../datasets/mini_sounds',
        type=str,
        help='Directory path of CVS data')
    parser.add_argument(
        '--samples_class',
        default=20,
        type=int,
        help='Number of isntances to be loaded for class')   
    parser.add_argument(
        '--reuse_pickle',
        default=False,
        type=bool,
        help='Checks if DS has already been loaded')
    parser.add_argument(
        '--clip_len',
        default=10,
        type=int,
        help='Checks if DS has already been loaded')
    return parser.parse_args() 

def main():
    args = get_arguments()

    classes = []
    data = {}

    # Read classes on DS
    with open(join(args.data_path, 'stat.csv')) as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            classes.append(row[0])

    # Read DS info
    with open(join(args.data_path, 'vggsound.csv'))as f:
        csv_reader = csv.reader(f)
        for item in csv_reader:
            if item[2] in classes:
                data = update_data(data, *item)

    # Create a miniDS with n sampels per class
    mini_set_path = args.ds_path + '_' + str(args.samples_class)+'.pickle'
    
    if exists(mini_set_path) and args.reuse_pickle:
        with open(mini_set_path, 'rb') as handle:
            mini_data = pickle.load(handle)
    else:
        black_list = {}
        to_remove = [0]
        while(len(to_remove)):
            mini_data = build_test_dataset(data, black_list, args.samples_class)
            mini_data, to_remove = get_video(mini_data, args.ds_path, args.clip_len)
            black_list.update(to_remove)
        with open(mini_set_path, 'wb') as handle:
            pickle.dump(mini_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # extrac audio from videos
        get_audio(mini_data, args.ds_path)
        get_frames(mini_data, args.ds_path, args.clip_len)

    print('DataSet completed')

if __name__ == "__main__":
    main()

