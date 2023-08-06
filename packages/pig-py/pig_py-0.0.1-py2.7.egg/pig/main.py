#!/usr/bin/python3

from PIL import Image
from resizeimage import resizeimage
from utils.io import Io
import json
from pprint import pprint

# create folders to android
Io.createFolders('resources/android/icon')
Io.createFolders('resources/android/splash')

# create folders to ios
Io.createFolders('resources/ios/icon')
Io.createFolders('resources/ios/splash')

with open('dimensions.config.json') as f:
  data = json.load(f)


for platform in data:
  logo = Image.open('splash.png', 'r')
  logo_w, logo_h = logo.size

  #create icons
  for image in platform['icon']['images']:
    if logo_h > logo_w:
      height = 0.6 * image['dimensions'][1]
      width = (logo_w * height) / logo_h
    else:
      width = 0.8 * image['dimensions'][0]
      height = (logo_h * width) / logo_w

    brand = resizeimage.resize_cover(logo, [width, height])
    brand_w, brand_h = brand.size

    background = Image.new('RGBA', (image['dimensions'][0], image['dimensions'][1]), (255, 255, 255, 255))
    bg_w, bg_h = background.size

    offset = ((bg_w - brand_w) // 2, (bg_h - brand_h) // 2)
    background.paste(brand, offset)

    filename = platform['icon']['output'] + '/' + image['name'] + '.png'
    background.save(filename, 'png')
    pprint('icon created ==>> ' + filename)

  for image in platform['splash']['images']:
    if logo_h > logo_w:
      height = 0.6 * image['dimensions'][1]
      width = (logo_w * height) / logo_h
    else:
      width = 0.8 * image['dimensions'][0]
      height = (logo_h * width) / logo_w

    if (logo_h < height) | (logo_w < width):
      brand = logo
    else:
      brand = resizeimage.resize_cover(logo, [width, height])
    
    brand_w, brand_h = brand.size

    background = Image.new('RGBA', (image['dimensions'][0], image['dimensions'][1]), (255, 255, 255, 255))
    bg_w, bg_h = background.size

    offset = ((bg_w - brand_w) // 2, (bg_h - brand_h) // 2)
    background.paste(brand, offset)

    filename = platform['splash']['output'] + '/' + image['name'] + '.png'
    background.save(filename, 'png')
    pprint('splash created ==>> ' + filename)
  
