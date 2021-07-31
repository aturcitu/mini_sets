from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import moviepy.editor as mp

from pytube import YouTube
from tqdm import tqdm

from os.path import join, exists
import os

from shutil import copyfile
import random

import multiprocessing 
import subprocess


def prepare_clip_zero_shoot(data, ds_path, frame_num = 5):
    classes = []
    clip_tuple = []
    for video_key, obj_info  in data.items():
            class_label = obj_info['label']
            if class_label not in classes:
                classes.append(class_label)
            clip_tuple.append([join(ds_path, class_label, video_key)+'_'+str(frame_num)+'.png', class_label])
    return clip_tuple, classes

 
def create_ds_tuple(data, tuple_length = 3):
    tuple = {}
    classes = []
    i = 0
    while(i<tuple_length):       
        random_key, random_obj = random.choice(list(data.items()))
        class_label = data[random_key]['label'] 
        if class_label not in classes:
            classes.append(class_label)
            tuple.update({random_key: random_obj})
            i = i + 1 
    return tuple


def prepare_clip_tuple(data, ds_path, test_length = 3):
    test_clip_tuple = [] 
    for i in range (test_length):
        clip_tuple = [] 
        tuple = create_ds_tuple(data, tuple_length = 3)
        for video_key, obj_info  in tuple.items():
                class_label = obj_info['label']
                clip_tuple.append([join(ds_path, class_label,video_key)+'_5.png',class_label])
        test_clip_tuple.append(clip_tuple)
    return test_clip_tuple


def build_test_dataset(data, delete_data, samples_class = 3):
    mini_data={}
    class_count = {}
    for video_key, obj_info  in data.items():
        if video_key not in delete_data: 
            class_label = obj_info['label']
            if class_label in class_count:
                if class_count[class_label] < samples_class:
                    mini_data.update({video_key: obj_info})
                    class_count[class_label] = class_count[class_label] + 1
            else:
                mini_data.update({video_key: obj_info})
                class_count.update({class_label: 1})
    return mini_data


def update_data(data, video_id, start, label, split):
    """
    Updates the annotations dict with by adding the desired data to it

    :return: the updated dictionary
    """

    video_key = video_id
    obj_info = dict(
        label = label,        
        start = int(start),
        split = split
    )

    if video_key not in data.keys():
        data.update({video_key: obj_info})

    return data

def get_frames(data, download_path, video_length):
    for video_id, video_obj in tqdm(data.items(), desc="Extracting frames from video"):
        get_frames_en = 0
        class_label = video_obj['label']
        
        for t in range(int(video_length)):
            if not exists(join(download_path, class_label, video_id)+'_'+str(t)+'.png'):
                get_frames_en = 1
        
        if get_frames_en: 
            video_path = join(download_path, class_label, video_id)+'.mp4'
            try:
                video = mp.VideoFileClip(video_path)
            except OSError:
                try:
                    os.remove(video_path)
                    print('Delete:',video_path)
                except FileNotFoundError:
                    print('Not Found:',video_path)
            else:
                for t in range(int(video_length)):
                    frame_path = join(download_path, class_label, video_id)+'_'+str(t)+'.png'
                    if not exists(frame_path):
                        try:
                            video.save_frame(frame_path, t = t)
                        except OSError:
                            print('frame:',frame_path,'failed.')    

def convert(v):
    subprocess.check_call([
    'ffmpeg',
    '-n',
    '-i', v,
    '-acodec', 'pcm_s16le',
    '-ac','1',
    '-ar','16000',
    '%s.wav' % v[:-4]])
  

def get_audio(data, download_path):
    files = []
    for video_id, video_obj in tqdm(data.items(), desc="Extracting audio from video"):
        class_label = video_obj['label']
        if not exists(join(download_path, class_label, video_id)+'.wav'):
            #delete
            #os.remove(join(download_path, class_label, video_id)+'.wav')
            files.append(join(download_path, class_label, video_id)+'.mp4')
            #video = mp.VideoFileClip(join(download_path, class_label, video_id)+'.mp4')
            #video.audio.write_audiofile(join(download_path, class_label, video_id)+'.wav', 44100, 2, 2000,"pcm_s32le")
    p = multiprocessing.Pool(32)
    p.map(convert, files)


def get_video(data, download_path, seconds_long):
    to_remove = {}
    
    youtube_path = 'https://www.youtube.com/watch?v='

    for video_id, video_obj in tqdm(data.items(), desc="Collecting data from YT"):
        class_label = video_obj['label']
        video_url = youtube_path+video_id
        yt = YouTube(video_url)
        if not exists(join(download_path, class_label)):
            os.mkdir(join(download_path, class_label))
        if not exists(join(download_path, class_label, video_id)+'.mp4'):
            #print('Downloading video')
            try:
                # Download 
                video = yt.streams.filter(progressive=True, file_extension='mp4').first()
                video.download(join(download_path, class_label))
            except:
                print('Connection Error')
                to_remove.update({video_id: video_obj})
            else:
                # Cut clip 
                ffmpeg_extract_subclip(join(download_path, class_label, video.default_filename), video_obj['start'], video_obj['start']+seconds_long, join(download_path, class_label, video_id)+'.mp4')
                # Delelete long video
                os.remove(join(download_path, class_label, video.default_filename))
    
    return data, to_remove




        