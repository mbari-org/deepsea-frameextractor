#!/usr/bin/env python

__author__ = "Danelle Cline"
__copyright__ = "Copyright 2020, MBARI"
__credits__ = ["MBARI"]
__license__ = "GPL"
__maintainer__ = "Danelle Cline"
__email__ = "dcline at mbari.org"
__doc__ = '''

Utility for swapping ymin/ymax in annotation xml files

@author: __author__
@status: __status__
@license: __license__
'''

import sys
import os
import subprocess
import glob
import shutil

def process_command_line():
  import argparse
  from argparse import RawTextHelpFormatter

  examples = 'Examples:' + '\n\n'
  examples += sys.argv[0] + "-s 'python clean.py' " \
                            "-i /mnt/RAID/data/imgs/annotations "
  parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                   description='Extract still jpeg frames from video',
                                   epilog=examples)
  parser.add_argument('-i', '--input_dir', action='store', help='full path to base directory where prores files are',
                      default='', required=True)
  args = parser.parse_args()
  return args

if __name__ == '__main__':
  args = process_command_line()

  for xml_in in glob.iglob(args.input_dir + '/*.xml'):
    print('Found {}'.format(xml_in))
    with open(xml_in, 'r') as myfile:
      data = myfile.read().replace('\n', '')
      if 'ymin' in data and 'ymax' in data:
        command = "sed -i .bak  " \
              "'s#ymin#YMAX#g;" \
              "s#ymax#YMIN#g;" \
              "s#YMAX#ymax#g;" \
              "s#YMIN#ymin#g;' {} ".format(xml_in)
        print(command)
        subprocess.Popen(command, env=os.environ, shell=True)
