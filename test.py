
# importing the module 
from pytube import YouTube 
  
URL = "https://www.youtube.com/watch?v=80SsC_ZNbyI"
video = YouTube(URL)
video_streams = video.streams
print(video_streams)