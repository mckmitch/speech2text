from moviepy.editor import *
import glob  # Similar to os module, gives list of files in the directory and makes it easy to find
import os
from pprint import pprint as pp  # Pretty print module

# print(glob.glob("video/*.mp4"))
output_dir = "audio"

for file in glob.glob("video/*.mp4"):
    # print(file)
    videoclip = VideoFileClip(file)  # Load the video file object into a var
    audioclip = videoclip.audio

    # audioclip.write_audiofile(file[:-3]+"mp3")
    filename = os.path.basename(file)
    # Changing the output directory to /audio
    output_file = os.path.join(output_dir, os.path.splitext(filename)[0] + ".mp3")
    audioclip.write_audiofile(output_file)

# print(dir(videoclip))
# pp(dir(videoclip))
# pp(dir(videoclip.audio))