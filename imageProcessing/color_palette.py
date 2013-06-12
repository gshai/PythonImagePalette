import Image, ImageOps

import ImageChops
import ImageEnhance
import ImageDraw
import ImageFilter
import logging

from StringIO import StringIO
import urllib

import sys
import operator
from operator import itemgetter
from math import sqrt
import colorsys 
from itertools import groupby
from Flask import send_file

# Author Gilad Shai
# email spotted.rhino.inc@gmail.com
# url http://spottedrhino.com

RECT = (0,0,100,100)
FILTER_MODE = 10
HIST_ELEMENTS = 100
DEBUG = True

def fetch(url):
  	img = Image.open(StringIO(urllib.urlopen(url).read()))  	
  	return img
 
def histogram_for_url_and_rect(url):
	print "histogram_for_url_and_rect: ", url
	im = fetch(url)
	logging.info('got the image for url')
	#im = Image.open(im_url)
	rect = (im.size[0]/2-50, im.size[1]/4, im.size[0]/2 + 50, im.size[1]/4 + 100)
	bg = histogram_for_image_and_rect(im, rect)
	
	img_io = StringIO()
	bg.save(img_io, 'JPEG', quality=70)
	img_io.seek(0)
	return send_file(img_io, mimetype='image/jpeg')
	#return bg
	
def histogram_for_image_and_rect(image, rect=RECT):
	''' starting point. receives image and rect to crop 
	and create a histogram/color pallete'''
	print ("histogram_for_image_and_rect: ", rect)	
	thumb = _crop_image(image, rect)
	thumbSmoth = thumb.filter(ImageFilter.SMOOTH)
	thumbMode = thumbSmoth.filter(ImageFilter.ModeFilter(FILTER_MODE))	
	
	# get dominate colors
	list = _color_histogram_image(thumbMode, HIST_ELEMENTS)
	
	# generate image from dominate colors
	bg = fill_image_from_list(list,(1000,100))
	if DEBUG:
		logging.info('debug')
		bg.show()
		thumb.show()
		thumbMode.show()
	return bg


def _crop_image(image, rect):
	print"_crop_image", rect
	thumb = image.crop(rect)
	#thumb.save('thumb.jpg')
	return thumb

def _histogram_image(image):
	'''histogram returns a list (array) of pixel values 0-255.
	the indexes 0-255 RED 256-511 GREEN 512-768 BLUE'''
	list = image.histogram()
	return list

def _color_histogram_image(image, n=3):
	'''get color returns a list of tuples with appearance and RGB'''
	alist = image.getcolors(image.size[0] * image.size[1])		
	alist.sort(key=itemgetter(0), reverse=True)
	if n < 0:
		n = len(alist)-2
		print "n: ", n
	colorList = map(itemgetter(1), alist[:n])	
	return colorList

def fill_image_from_list(alist=[(255,255,0)],size=(100,100)):
	print "fill_image_from_list"
	
	baseList = [alist[0],]
	for i in range(1, len(alist)):
		matches = 0
		for hue in baseList:
			distance = sqrt(sum((a-b)**2 for a,b in zip(hue, alist[i])))
			print "distance: ", distance			
			if distance > 50:
				matches = matches+1
			else:
				continue
			if matches == len(baseList):
				baseList.append(alist[i])
				print "base list: ", baseList
		print "------------------------"
	
	bg = Image.new('RGB', size, (0,255,0))	 
	bg_w,bg_h = bg.size
	img_w = bg_w/len(baseList)
	img_h = bg_h	
	
	#add a strips
	for i in range(0, len(baseList)):
		offset = ((bg_w-img_w*(i+1)), 0)
  		strip = Image.new('RGB', (img_w,img_h), baseList[i])
  		print "base: ", baseList[i]
 	  	bg.paste(strip, offset)
 		
	#bg.save('colors.jpg')
	return bg
	
def _color_exp():
	size=(1000,100)
	bg = Image.new('RGB', size, (0,255,0))	 
	bg_w,bg_h = bg.size
	img_w = bg_w/255
	img_h = bg_h	

	for i in range(1, 255):
		offset = ((bg_w-img_w*i), 0)
		offset2 = ((bg_w-img_w*i), 50)
		hsv = colorsys.rgb_to_hsv(i, 100, 100)
		print "hsv :", hsv		
		strip1 = Image.new('RGB', (img_w,img_h/2), (i, 100, 100))
# 		strip2 = Image.new('RGB', (img_w,img_h/2), colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2]))
		rgb = hsvToRGB(hsv[0], hsv[1], hsv[2])
		rgb1 = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
		print "rgb: ", rgb
		strip2 = Image.new('RGB', (img_w,img_h/2), rgb1)
 		bg.paste(strip1, offset)
 		bg.paste(strip2, offset2)
 	bg.show()

def hsvToRGB(h, s, v):
    """Convert HSV color space to RGB color space
    
    @param h: Hue
    @param s: Saturation
    @param v: Value
    return (r, g, b)  
    """
    import math
    hi = math.floor(h / 60.0) % 6
    f =  (h / 60.0) - math.floor(h / 60.0)
    p = v * (1.0 - s)
    q = v * (1.0 - (f*s))
    t = v * (1.0 - ((1.0 - f) * s))
    return {
        0: (v, t, p),
        1: (q, v, p),
        2: (p, v, t),
        3: (p, q, v),
        4: (t, p, v),
        5: (v, p, q),
    }[hi]

def rgbToHSV(r, g, b):
    """Convert RGB color space to HSV color space
    
    @param r: Red
    @param g: Green
    @param b: Blue
    return (h, s, v)  
    """
    maxc = max(r, g, b)
    minc = min(r, g, b)
    colorMap = {
        id(r): 'r',
        id(g): 'g',
        id(b): 'b'
    }
    if colorMap[id(maxc)] == colorMap[id(minc)]:
        h = 0
    elif colorMap[id(maxc)] == 'r':
        h = 60.0 * ((g - b) / (maxc - minc)) % 360.0
    elif colorMap[id(maxc)] == 'g':
        h = 60.0 * ((b - r) / (maxc - minc)) + 120.0
    elif colorMap[id(maxc)] == 'b':
        h = 60.0 * ((r - g) / (maxc - minc)) + 240.0
    v = maxc
    if maxc == 0.0:
        s = 0.0
    else:
        s = 1.0 - (minc / maxc)
    return (h, s, v)		
		
def main(argv):
	print argv[1]
	im = Image.open(argv[1])	
	rect = (im.size[0]/2-50, im.size[1]/4, im.size[0]/2 + 50, im.size[1]/4 + 100)
	histogram_for_image_and_rect(im, rect)

if __name__ == "__main__":
   main(sys.argv)
   #_color_exp()
''' 
	Hue [0-1] radians 
	m = Min(r,g,b)
	M = Max(r,g,b)
	C = M-m   		natural colors|C==0
	if M==r H=60*(G-B)/C
	if M==g H=60*(B-R)/C
	if M==b H=60*(R-G)/C
	 Saturation = 0 if C==0; C/V else
	 Value [0-1]
'''

   