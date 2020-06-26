#!/usr/bin/env python
__author__ = 'Danelle Cline'
__copyright__ = '2020'
__license__ = 'GPL v3'
__contact__ = 'dcline at mbari.org'
__doc__ = '''

Utility class  

@var __date__: Date of last svn commit
@undocumented: __doc__ parser
@status: production
@license: GPL
'''
 
import os 
import subprocess 
import re
  
def get_dims(image):
    """
    get the height and width of a tile
    :param image: the image file
    :return: height, width
    """
    cmd = 'identify "%s"' % (image)
    subproc = subprocess.Popen(cmd, env=os.environ, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                               stdout=subprocess.PIPE)
    out, err = subproc.communicate()
    # get image height and width of raw tile
    p = re.compile(r'(?P<width>\d+)x(?P<height>\d+)')
    match = re.search(pattern=p, string=out)
    if (match):
        width = match.group("width")
        height = match.group("height")
        return height, width

    raise Exception('Cannot find height/width for image %s' % image)

def get_framerate(video_file):
    """
       get the frame rate of a video file
       :param video_file: the video file
       :return: height, width
       """
    cmd = 'ffprobe -i {}'.format(video_file)
    print(cmd)
    subproc = subprocess.Popen(cmd, env=os.environ, shell=True, stdin=subprocess.PIPE, 
                               stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = subproc.communicate() 
    print(out)
    print(err)
    # many thanks to https://regexr.com/ for helping simplify testing these expressions !
    p = re.compile('(\d?.\d) fps')
    match = re.search(pattern=p, string=str(err))
    if (match):
        fps = float(match.groups(0)[0])
        return fps

    raise Exception('Cannot find frame rate for image {}'.format(video_file))

def ensure_dir(d):
    """
    ensures a directory exists; creates it if it does not
    :param fname:
    :return:
    """
    if not os.path.exists(d):
        os.makedirs(d)
  
def f_exists(fname):
    """
    checks if a file exists
    :param fname: 
    :return: 
    """
    try:
        with open(fname) as f:
            return True
    except IOError:
        return False 

def wrapper(func, *args, **kwargs):
    '''
    utility function to warp arguments
    :param args: 
    :param kwargs: 
    :return: t
    '''
    def wrapped():
        return func(*args, **kwargs)

    return wrapped

def validate_iso8601(str):
    '''
    Validates whether string is in compressed ISO8601 format, e.g. 20080830T014536
    :param str: 
    :return: True if valid
    '''
    import re
    regex = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})(1[0-2]|0[1-9])(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9])([0-5][0-9])([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'
    match_iso8601 = re.compile(regex).match
    try:            
        if match_iso8601(str) is not None:
            return True
    except:
        pass
    return False


def get_length(input_video_path):
    '''
    gets the length of a video in seconds using ffprobe
    :return: length: length of video in nearest seconds found at self.input_video_path
    :rtype   length: int
    '''
    #TODO: check if URL valid
    if 'http' not in input_video_path and not os.path.exists(input_video_path):
        raise Exception('{} does not exist'.format(input_video_path))

    shell_string = "ffprobe -i {} -show_entries format=duration -v quiet -of csv='p=0'".format(input_video_path)
    result = subprocess.Popen(shell_string,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              shell=True)
    length = result.communicate()[0]
    length = int(round(float(length.decode().strip('\n'))))
    return length
