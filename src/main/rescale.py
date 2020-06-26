#!/usr/bin/env python

__author__ = "Danelle Cline"
__copyright__ = "Copyright 2020, MBARI"
__credits__ = ["MBARI"]
__license__ = "GPL"
__maintainer__ = "Danelle Cline"
__email__ = "dcline at mbari.org"
__doc__ = '''

Utility for rescaling xml files 

@author: __author__
@status: __status__
@license: __license__
'''
import cv2
import sys
import os
import glob
import shutil
from bs4 import BeautifulSoup, Tag
from xml.dom.minidom import parse

def process_command_line():
  import argparse
  from argparse import RawTextHelpFormatter

  examples = 'Examples:' + '\n\n'
  examples += sys.argv[0] + "-s 'python rescale.py' " \
                            "-i /mnt/RAID/data/imgs/annotations "
  parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter,
                                   description='Deinterlace and rescale images',
                                   epilog=examples)
  parser.add_argument('-i', '--input_dir', action='store', help='full path to base directory where prores files are',
                      default='', required=True)
  parser.add_argument('-l', '--label', action='store', help='label to assign to saliency',
                      default='', required=False)
  args = parser.parse_args()
  return args

if __name__ == '__main__':
  args = process_command_line()
  width = 960
  height = 540
  for xml_in in glob.iglob(args.input_dir + '/*.xml'):
    print('Found {}'.format(xml_in))
    with open(xml_in, 'r') as myfile:
        soup = BeautifulSoup(myfile.read(), 'xml')
        root = os.path.basename(xml_in).split('.')[0]
        scale_width = float(width/float(soup.annotation.size.width.string))
        scale_height = float(height/float(soup.annotation.size.height.string))
        soup.size.width.string = str(width) 
        soup.size.height.string = str(height)
 
        # deinterlace
        parent_path = xml_in.split(soup.annotation.folder.string)[0] + soup.annotation.folder.string
        image_path = '{}/{}.png'.format(parent_path, root)
        img = cv2.imread(image_path)
        if img is None:
          os.remove(xml_in)
          continue
        h, w, channels = img.shape
        print('Reading {} {}x{}'.format(image_path, h, w))

        if h != height and w != width and h == 1080 and w == 1920:
          print('Deinterlacing {} {}x{} to {}x{}'.format(root, h, w, height, width))
          org_path = '{}/{}.png.bak'.format(parent_path, root)
          shutil.copyfile(image_path, org_path)
          de_interlaced_img = img[::2, 1::2]
          cv2.imwrite(image_path, de_interlaced_img)
          h, w, channels = de_interlaced_img.shape

        if h < height or w < width:
          print('Rescaling {} {}x{} to {}x{}'.format(root, h, w, height, width))
          resized_image = cv2.resize(img, (width, height))
          h, w, channels = resized_image.shape
          cv2.imwrite(image_path, resized_image)

        # replace saliency with the label
        objects = soup.find_all('object')
        for o in objects:
          tag_name = o.find('name')
          if 'saliency' in tag_name.string or 'Saliency' in tag_name.string :
            tag_name.string = args.label
            o.bndbox.xmin.string = str(int(round(float(o.bndbox.xmin.string)) * scale_width))
            o.bndbox.xmax.string = str(int(round(float(o.bndbox.xmax.string)) * scale_width))
            o.bndbox.ymin.string = str(int(round(float(o.bndbox.ymin.string)) * scale_height))
            o.bndbox.ymax.string = str(int(round(float(o.bndbox.ymax.string)) * scale_height))

    xml_out = 'tmp.xml'
    if xml_out == xml_in:
      raise Exception('{} will be overwritten'.format(xml_out))

    print('Writing ' + xml_out)
    f = open('tmp.xml', "w")
    f.write(soup.decode_contents())
    f.close()

    # a bit of hacky workaround to print a better looking xml than what beautifulsoup produces
    xmlf = parse('tmp.xml')
    pretty_xml_as_string = xmlf.toprettyxml()
    shutil.copyfile(xml_in, xml_in + '.bak')
    xml_out = xml_in
    # remove empty lines
    pretty_xml_as_string = os.linesep.join([s for s in pretty_xml_as_string.splitlines() if s.strip()])
    with open(xml_out, 'w') as f:
      f.write(pretty_xml_as_string)
    f.close()
