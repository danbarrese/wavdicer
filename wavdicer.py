# WAV DICER
# Author: Dan Barrese (danbarrese.com)
# Version: 0.80
# Description: Dices a single wave file into many wave files.
#
# Update History:
# 2014.02.04 [DRB][0.00]   Created.
# 2014.02.05 [DRB][0.80]   Added CLI, parsing for input params.

import wave
import struct
import argparse

def format_track_num(track_number):
    """Formats a track number as two digits with leading 0 if needed."""
    return str(track_number).rjust(2, str(0))

def convert_timestr_to_seconds(timestr):
    """Converts time string formatted like 1:20 (1 min, 20 sec) into a decimal."""
    arr = timestr.split(":")
    m = int(arr[0])
    s = int(arr[1])
    return (60.0 * m) + s

def convert_many_timestr(timestrings):
    """Converts time strings (like '1:20 1:36') delimited by a space."""
    stimes = timestrings.split(" ")
    itimes = []
    for timestr in stimes:
        itimes.append(convert_timestr_to_seconds(timestr))
    return itimes

parser = argparse.ArgumentParser(description='Dices a single wave file into multiple wave files.')
parser.add_argument('--input', type=str, nargs=1,
        dest='path', metavar='P', required=True,
        help='Path to the input wave file.')
parser.add_argument('--times', type=str, nargs=1,
        dest='times_input', metavar='T', required=True,
        help='Lengths of output wave files, e.g. "1:04 4:31 10:13" (with quotes).')

args = parser.parse_args()

# Input.
times_input = args.times_input
split_times = convert_many_timestr(times_input)
path = args.path

# Setup.
track_name = 'Track'
track_number = 1
lastslash = path.rfind("/") + 1
dir = path[0:lastslash]
input_filename = path[lastslash:]
output_ext = path[path.rfind(".") + 1]

# Read audio params.
audio = wave.open(dir + input_filename, 'r')
channels = audio.getnchannels()
sample_width = audio.getsampwidth()
framerate = audio.getframerate()
frames = audio.getnframes()
seconds_total = frames/framerate
print('Channels: ' + str(channels))
print('Sample width: ' + str(sample_width))
print('Frequency: ' + str(framerate))
print('Frames: ' + str(frames))
print('Seconds: ' + str(seconds_total))

# Scan audio file passively until non-silence is encountered.
non_silence_frame = 0
for i in range(0, frames):
    waveData = audio.readframes(1)
    data = struct.unpack("<h", waveData)
    frameval = int(data[0])
    if frameval > 0:
        non_silence_frame = i
        break

# Rewind to (up to) 0.5 seconds before first non silence frame.
frame_to_start_recording = non_silence_frame - (0.5 * framerate)
audio.rewind()
if frame_to_start_recording > 0:
    audio.readframes(frame_to_start_recording)

# Split audio file into pieces, save each piece to separate file.
for i in range(0, len(split_times)):
    # Get wave audio data for an entire track length.
    track_length = split_times.pop(0)
    if track_length <= 0.0:
        track_length = 36000.0 #10 hours
    waveData = audio.readframes(int(track_length * framerate))

    # Write audio data to file.
    output = wave.open(dir + track_name + format_track_num(track_number) + "." + output_ext, 'w')
    output.setnchannels(channels)
    output.setsampwidth(sample_width)
    output.setframerate(framerate)
    output.writeframesraw(waveData)
    output.close()
    print('Finished writing ' + track_name + format_track_num(track_number))
    track_number += 1
