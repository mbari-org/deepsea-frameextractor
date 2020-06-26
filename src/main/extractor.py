#!/usr/bin/env python

__author__ = "Danelle Cline, Nathanial Yee"
__copyright__ = "Copyright 2020, MBARI"
__credits__ = ["MBARI"]
__license__ = "GPL"
__maintainer__ = "Danelle Cline"
__email__ = "dcline at mbari.org"
__doc__ = '''

Utility module for converting video to still frames and deinterlacing using the ffmpeg module

@author: __author__
@status: __status__
@license: __license__
'''

import logging
from logging import handlers
import sys
import os
import utils  
import multiprocessing
import subprocess 
import cv2
import signal
import re 
from datetime import datetime, timedelta 
import glob

class Extractor():
    def __init__(self, input_video_path, output_dir, deinterlace='drop', step=5, duration=1000, start=None, end=None, prefix=None):
        '''
        the Extractor class contains all the necessary information to extract
        images from a video using ffmpeg. By default, it will extract a frame
        every step (5) seconds from the video

        :param input_video_path:  full path to the video
        :param output_dir: directory to store transcoded frames to
        :param step: extract a frame every 'step' seconds
        :param duration: duration in milliseconds to extract every step seconds
        :param start: starting time to extracting images
        :param end: ending time to finish extracting images
        :param prefix: frame starting prefix to prepend to extracted frames
        
        :Example:
        Extract every 5th frame using drop deinterlacing
        Extractor('/Volumes/data/D008_03HD.mov', '/Volumes/data/out/D008_03HD', 'drop', 5)
        '''
        self.input_video_path = input_video_path
        _, fname = os.path.split(input_video_path)
        self.key = fname.split('.')[0]
        self.output_dir = '{0}/{1}/imgs'.format(output_dir, self.key)
        utils.ensure_dir(self.output_dir)
        self.seconds_counter = 0
        self.duration = duration
        self.step = step
        self.start = start
        self.end = end
        self.prefix = prefix
        self.video_length = utils.get_length(input_video_path)
        self.fps = 29.97 #utils.get_framerate(input_video_path)
        self.single_frame = False
        if duration is None:
            self.duration = 1e3/self.fps + 1  # default to a single frame
            self.single_frame = True
        if prefix is None:
            self.prefix = "f"
        # To time methods, uncomment line below
        #self.times = []
        self.deinterlace = deinterlace 
        self.start_iso_time = datetime.now()
        self.dive = 'Unknown'
        p = fname.split('_')
        for f in p:
            if utils.validate_iso8601(f): 
                self.start_iso_time = datetime.strptime(f, '%Y%m%dT%H%M%SZ')
                break
        if 'D' in fname:
            p = re.compile(r'(?P<dive>\w+)_(?P<timecode>\w+)?')
            match = re.search(pattern=p, string=fname)
            if (match):
                if match.group('timecode') and utils.validate_iso8601(match.group('timecode')):
                    self.start_iso_time = datetime.strptime(match.group('timecode'), '%Y%m%dT%H%M%SZ')
                else:
                    self.start_iso_time = datetime.now()
                if match.group('dive'):
                    self.dive = match.group('dive') 
    
        print('Dive {} timecode start {} length {} seconds'.format(self.dive, self.start_iso_time, self.video_length))  
    
    def __del__(self):
        print('Done')
        # To time methods, uncomment line below
        #if self.times and len(self.times) > 0:
        #    import numpy as np
        #    m = np.array(self.times)
        #    print('Mean {}'.format(m.mean()))

    def extract_all_images(self, start, end):
        '''
        extracts image(s) from video between timecodes and saves it to output_path
        :param start:  starting time
        :param end:  ending time
        :return: total frames extracted
        :Example:
        self.extract_all_images('00:11:40', '00:11:41')
        '''
        timecode_str = '{0:02}:{1:02}:{2:02}.{3:03}'.format(start.hour, start.minute, start.second,
                                                            int(start.microsecond / 1e3))
        output_path = '{}/{}%06d.png'.format(self.output_dir, self.prefix)
        frames = int((end - start).total_seconds() * self.fps)
        if self.deinterlace == 'drop':
            shell_string = 'ffmpeg -y -re -loglevel error -accurate_seek -ss {} -i {} -an -frames:v {} {}'.format(timecode_str,
                                                                       self.input_video_path, frames, output_path)
            print(shell_string)
            subprocess.call(shell_string, shell=True)
            for i in glob.glob('{}/{}*.png'.format(self.output_dir, self.prefix)):
                # retain 16-bit depth if exists
                img = cv2.imread(i, cv2.IMREAD_UNCHANGED)
                de_interlaced_img = img[::2, 1::2]
                cv2.imwrite(i, de_interlaced_img)
        elif self.deinterlace == 'yadif':
            shell_string = 'ffmpeg -y -re -loglevel error -accurate_seek -ss {} -i {} -vf yadif=1:-1:0 -an -frames:v {} {}'.\
                                                                        format(timecode_str,
                                                                       self.input_video_path, frames, output_path)
            subprocess.call(shell_string, shell=True)
        else:
            shell_string = 'ffmpeg -y -re -loglevel error -accurate_seek -ss {} -i {} -an -frames:v {} {}'.format(timecode_str,
                                                                                                 self.input_video_path,  frames, output_path)
            subprocess.call(shell_string, shell=True)

        return int((end - start).total_seconds() * self.fps)
        '''frames = int((end - start).total_seconds() * self.fps)
        inc_microseconds = int(1e6/self.fps)
        dt = self.start_iso_time + timedelta(seconds=start.second)
        for i in range(frames):
            output_path = '{0}/{1}_{2:03}.png'.format(self.output_dir,filename_prefix, i+1)
            s = dt.strftime('%Y%m%dT%H%M%S.%f')
            dt_iso_str = s[:-3] + 'Z' #here we simply truncate; this may be off by by half a millisecond
            print('Datetime {}'.format(dt_iso_str))
            shell_string = 'exiftool -config mbari.config -PNG:Dive="{}" -PNG:Datetime="{}" {}'.format(self.dive, dt_iso_str, output_path)
            subprocess.call(shell_string, shell=True, stdout=file_out, stderr=file_out)
            output_path_original = '{}_original'.format(output_path)
            os.remove(output_path_original)
            dt += timedelta(microseconds=inc_microseconds)'''

    def extract_images(self, start, end):
        ''''
        extracts image(s) from video at timecode and saves it to output_path
        :param start:  starting time
        :param end:  ending time
        :return:
        :Example:
        self.extract_images('00:11:40', '00:11:41')
        '''
        file_out = open('/dev/null', 'w')
        filename_prefix = '{0}_{1:02}-{2:02}-{3:02}'.format(self.key, start.hour, start.minute, start.second)
        timecode_str = '{0:02}:{1:02}:{2:02}.{3:03}'.format(start.hour, start.minute, start.second, int(start.microsecond/1e3))
        frames = int((end - start).total_seconds() * self.fps)
        if self.single_frame:
            output_path = '{0}/{1}.png'.format(self.output_dir,filename_prefix)
        else:
            output_path = '{0}/{1}_%03d.png'.format(self.output_dir,filename_prefix)
        if self.deinterlace == 'drop':
            shell_string = 'ffmpeg -y -re -loglevel error -accurate_seek -ss {} -i {} -frames:v {} -an {}'.format(timecode_str,
                                                                       self.input_video_path, frames,
                                                                       output_path)
            subprocess.call(shell_string, shell=True, stdout=file_out, stderr=file_out)
            for i in glob.glob('{}/f*.png'.format(self.output_dir)):
                img = cv2.imread(i)
                de_interlaced_img = img[::2, 1::2]
                cv2.imwrite(i, de_interlaced_img)
        elif self.deinterlace == 'yadif':
            shell_string = 'ffmpeg -y -re -loglevel error -accurate_seek -ss {} -i {} -vf yadif=1:-1:0 -frames:v {} -an {}'.format(timecode_str,
                                                                       self.input_video_path, frames,
                                                                       output_path)
            subprocess.call(shell_string, shell=True, stdout=file_out, stderr=file_out)
        else: 
            shell_string = 'ffmpeg -y -re -loglevel error -accurate_seek -ss {} -i {} -frames:v {} -an {}'.format(timecode_str,
                                                                       self.input_video_path, frames,
                                                                       output_path)
            print(shell_string)
            subprocess.call(shell_string, shell=True, stdout=file_out, stderr=file_out)
             
        inc_microseconds = int(1e6/self.fps)
        dt = self.start_iso_time + timedelta(seconds=start.second)
        for i in range(frames):
            if self.single_frame:
                output_png = '{0}/{1}.png'.format(self.output_dir, filename_prefix)
            else:
                output_png = '{0}/{1}_{2:03}.png'.format(self.output_dir, filename_prefix, i+1)
            s = dt.strftime('%Y%m%dT%H%M%S.%f')
            dt_iso_str = s[:-3] + 'Z' #here we simply truncate; this may be off by by half a millisecond
            print('Datetime {}'.format(dt_iso_str))
            shell_string = 'exiftool -config /app/mbari.config -PNG:Dive="{}" -PNG:Datetime="{}" {}'.format(self.dive, dt_iso_str, output_png)
            print(shell_string)
            subprocess.call(shell_string, shell=True, stdout=file_out, stderr=file_out)
            original = '{}_original'.format(output_png)
            os.remove(original)
            dt += timedelta(microseconds=inc_microseconds)
        return frames

    def process_video(self):
        '''
        extract all the frames from video_name specified in __init__
        :return:
        '''
        try:
            # if not stepping through incrementally, process the range
            if self.step is None:
                if self.end:
                  end = self.end
                  #TODO put in check if this is within bounds of ending
                else:
                  end = self.start + timedelta(milliseconds=self.duration*1e3)

                start_str = self.start.strftime('%H:%M:%S.%f')[:-3]
                end_str = end.strftime('%H:%M:%S.%f')[:-3]
                print('Extracting image frames {} from {} to {} and saving to {}'.format(self.input_video_path,
                                                                                         start_str, end_str,
                                                                                         self.output_dir))
                total = self.extract_all_images(self.start, end)
            else:
                self.seconds_counter += self.start.hour*3600 * self.start.minute*60 + self.start.second
                start = self.start
                end = start + timedelta(milliseconds=self.duration)
                total = 0
                while self.seconds_counter < self.video_length:
                    # To time methods, uncomment line below
                    # import timeit
                    #func = utils.wrapper(self.extract_images, output_path, timecode)
                    #self.times.append(timeit.timeit(func, number=1))
                    if self.end and end > self.end:
                        break
                    start_str = start.strftime('%H:%M:%S.%f')[:-3]
                    end_str = end.strftime('%H:%M:%S.%f')[:-3]
                    print('Extracting image frame {} from {} to {} and saving to {}'.format(start_str, end_str,
                                                                                            self.input_video_path,
                                                                                            self.output_dir))
                    frames = self.extract_images(start, end)
                    start = start + timedelta(seconds=self.step)
                    end = start + timedelta(milliseconds=self.duration)
                    self.seconds_counter += self.step
                    print('Seconds {}'.format(self.seconds_counter))
                    total += frames
            print('Extracted {} total frames'.format(total))
            return True
        except Exception as ex:
            print(ex)
            return False

def process_command_line():
    import argparse
    from argparse import RawTextHelpFormatter

    examples = 'Examples:' + '\n\n'
    examples += sys.argv[0] + "-s 'python extractor.py' " \
                            "-i /Volumes/DeepLearningTests/benthic/ " \
                            "-o /Volumes/Tempbox/danelle/benthic/" \
                            "-k D0232_03HD_10s \n"
    examples += sys.argv[0] + "-s 'python extractor.py' " \
                            "-i /Volumes/DeepLearningTests/benthic/D0232_03HD_10s.mov " \
                            "-o /Volumes/Tempbox/danelle/benthic/ \n"
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                   description='Extract still jpeg frames from video',
                                   epilog=examples)
    parser.add_argument('-i', '--input', action='store', help='full path to base directory where video files are, or single video file. If using directory, specify glob to search for files', default='', required=True)
    parser.add_argument('-o', '--output_dir', action='store', help='full path to output directory to store frames', default='', required=False)
    # default to drop fields interlace if none specified
    parser.add_argument('-d', '--deinterlace', action='store', help='deinterlace choice, drop = drop fields, yadif = ffmpeg filter', required=False)
    parser.add_argument('-g', '--glob', action='store', help='List of glob search parameters to use to find files', nargs='*', required=False)
    parser.add_argument('-m', '--milliseconds', action='store', help='Number of milliseconds to capture every step', required=False, type=int)
    parser.add_argument('-s', '--step', action='store', help='Step size in seconds to grab a frame', required=False, type=int)
    parser.add_argument('-t', '--start', action='store', help='Start time in HH:MM:SS format', default="00:00:00", required=False)
    parser.add_argument('-e', '--end', action='store', help='End time in HH:MM:SS format', required=False)
    parser.add_argument('-p', '--prefix', action='store', help='Optional prefix to prepend to extracted filest', required=False)
    args = parser.parse_args()
    return args

def process_video(video, output_dir, deinterlace, milliseconds, step, start_time=None, end_time=None, prefix='f'):
    '''
    processes a video given its the name of the video
    :param video: absolute path or url to the input video to be processed 
    :param output_dir: absolute path of the output file
    :param deinterlace: deinterlacing method: drop or yadif 
    :param milliseconds: total milliseconds to extract every step seconds
    :param step: total in seconds to step through the video
    :param start_time: starting time to extracting images
    :param end_time: ending time to finish extracting images
    :param prefix: frame starting prefix to prepend to extracted frames
    :return:  True is success, False is exception

    :Example:
    process_video('/Volumes/DeepLearningTests/benthic/D0232_03HD_10s/D0232_03HD_10s.mov',
    '/Volumes/Tempbox/danelle/benthic/D0232_03HD_10s)
    '''
    print("Starting: {} saving to {} using deinterlacing method {} prefix {}".format(video, output_dir, deinterlace, prefix))
    extractor = Extractor(input_video_path=video, output_dir=output_dir, deinterlace=deinterlace, step=step,
                          duration=milliseconds, start=start_time, end=end_time, prefix=prefix)
    result = extractor.process_video()
    print("Finished: {}".format(video))
    return result

def process_helper(args):
    print('Running process helper with args {}'.format(args))
    return process_video(*args)

def sigterm_handler(signal, frame):
    print("extractor.py done")
    exit(0)

if __name__ == '__main__':

    args = process_command_line()

    if len(args.input) < 1:
        print ('Need to specify input directory -i or --input option')
        exit(-1)
    start_time = None
    end_time = None
    if args.start:
        if '.' in args.start:
            start_time = datetime.strptime(args.start, '%H:%M:%S.%f')
        else:
            start_time = datetime.strptime(args.start, '%H:%M:%S')
    if args.end:
        if '.' in args.end:
            end_time = datetime.strptime(args.end, '%H:%M:%S.%f')
        else:
            end_time = datetime.strptime(args.end, '%H:%M:%S')

    if not args.output_dir:
      output_dir = os.getcwd()
    else:
      output_dir = args.output_dir
 
    deinterlace_choices = ['drop', 'yadif'] 
    if args.deinterlace and args.deinterlace not in deinterlace_choices:
        print('{} not in {}'.format(args.deinterlace, deinterlace_choices))
        exit(-1)
 
    signal.signal(signal.SIGTERM, sigterm_handler)

    utils.ensure_dir(output_dir)
    try:
        if args.glob:
            print('CPU pool count {}; using {} CPUs'.format(multiprocessing.cpu_count(), multiprocessing.cpu_count() - 1))
            pool = multiprocessing.Pool(processes=multiprocessing.cpu_count() - 1)
            for pattern in args.glob:
                video_files = glob.iglob('{}/{}'.format(args.input,pattern))
                print(video_files)
                process_args = [(f, output_dir, args.deinterlace, args.milliseconds, args.step, start_time, end_time, args.prefix) for f in video_files]
            results = pool.map(process_helper, process_args)
        else:
            process_video(args.input, output_dir, args.deinterlace, args.milliseconds, args.step, start_time, end_time, args.prefix)
    
    except Exception as ex:
        print(ex) 
