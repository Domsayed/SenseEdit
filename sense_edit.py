"""
Sense HAT pixel art editor
No command line options
Save - appends edited image to a gallery json file in the current directory. 
"""
import sys
import os
import time
import logging
import json
from sense_hat import SenseHat, ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
yellow = (255, 255, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
#pink = (255, 105, 180)

#dark_grey = (64, 64, 64)
#grey = (128, 128, 128)
#light_grey = (192, 192, 192)

nothing = (0,0,0)

new = (192, 192, 192) #light_grey
save = (128, 128, 128)  #grey
load = (64, 64, 64)  #dark_grey

im = []
imMenu = [new, save, load, black, white, red, yellow, green, blue]
gallery = []

x = 7
y = 3

mode = 'menu' #edit', 'menu', 'show'

newCol = white
menuOffset = 0
gallery_depth =  None
lot = None

flash_stop = False

s = SenseHat()


def display(im, mode):
  pixels = []

  if mode == 'edit':
    # fill pixels with the image
    pixels = im
  elif mode == 'menu':
    # image we are editing on the left and menu on the right
    # ignore first n columns of image where n is width of menu
    for idx in range(0, 8):
      #print(idx)
      #print(im[idx * 8 + 1 : idx * 8 + 7], [imMenu[idx]])
      pixels.extend(im[idx * 8 + 1 : idx * 8 + 8])
      pixels.extend([imMenu[idx]])
      #print(pixels)
  elif mode == 'show':
    # menu on the left and image from gallery on the right
    for idx in range(0, 8):
      #print(idx)
      #print(im[idx * 8 + 1 : idx * 8 + 7], [imMenu[idx]])
      pixels.extend([imMenu[idx]])
      pixels.extend(im[idx * 8 : idx * 8 + 7])
      
  #print(pixels)
  
  #print(mode, x, y, newCol)
  
  # display the pixels  
  s.set_pixels(pixels)


def flash(cx, cy):
  global flash_stop

  if mode != 'show':
    col = s.get_pixel(cx, cy)
    if mode == 'edit':
      #print(col, newCol)
      if int(col[0] / 16) == int(newCol[0] / 16) and int(col[1] / 16) == int(newCol[1] / 16) and int(col[2] / 16) == int(newCol[2] / 16):
        # colours the same so show inverted
        #print(cx, cy, (255 - col[0], 255 - col[1], 255 - col[2]))
        if not flash_stop:
          s.set_pixel(cx, cy, (255 - col[0], 255 - col[1], 255 - col[2]))
      else:
        if not flash_stop:
          s.set_pixel(cx, cy, newCol)
    elif mode == 'menu':
      if not flash_stop:
        s.set_pixel(cx, cy, black)
    time.sleep(0.2)
    # reset colour
    if not flash_stop:
      s.set_pixel(cx, cy, col)
    time.sleep(0.2)
    #print(mode, cx, cy, newCol)
  flash_stop = False

def load_gallery():
  global gallery, gallery_depth
  #print('load gallery')
  
  gallery = []
  gallery_depth = 0
  
  if not os.access("gallery.json", os.R_OK):  
    return False
  with open("gallery.json", "r", encoding='utf-8') as gallery_file:
    #print('load json')
    gallery = json.load(gallery_file)
  #print('gallery: ', gallery)
  #print('len: ', len(gallery))
  if len(gallery) == 0:
    return False
  else:
    gallery_depth = len(gallery)
    if len(gallery) == 64:
      # there are 64 itmes in the list
      # but is this just one image 
      if len(gallery[0]) == 3: #check for RGB tuple
        # first item in the gallery is a pixel
        gallery_depth = 1
    return True
  

def append_gallery(imGal):
  global gallery, gallery_depth

  load_gallery()

  #print('add image to gallery')
  gallery.append(imGal)

  #print('write whole gallery')
  with open("gallery.json", "w", encoding='utf-8') as gallery_file:
    json.dump(gallery, gallery_file)
  gallery_depth = gallery_depth + 1


def fade():
  s.low_light = True


def bright():
  s.low_light = False


def acc_neg_count(a):
  return (1 if a['x'] < 0 else 0) + (1 if a['y'] < 0 else 0) + (1 if a['z'] < 0 else 0)


# call back functions for sensehat button
# down and up just change the Y
# left and right can also change the mode
def s_down(event):
  global y, lot

  #print('down')
  #print(event.direction, event.action)
  if event.action != ACTION_RELEASED:
    if mode == 'show':
      #print(mode, lot, gallery_depth)
      lot = (lot + 1) % gallery_depth
      imGal = gallery[lot]
      display(imGal, mode)
    else:
      #if mode == 'edit':
      #  s.set_pixel(x, y, im[x + y * 8])
      #elif mode == 'menu':
      #  s.set_pixel(x, y, imMenu[y])
      
      if y < 7:
        y = y + 1
    #print(mode, x, y, newCol)


def s_up(event):
  global y, lot

  #print('up')
  #print(event.action)
  if event.action != ACTION_RELEASED:
    if mode == 'show':
      #print(mode, lot, gallery_depth)
      lot = ((lot - 1) + gallery_depth) % gallery_depth
      imGal = gallery[lot]
      display(imGal, mode)
    else:
      #if mode == 'edit':
      #  s.set_pixel(x, y, im[x + y * 8])
      #elif mode == 'menu':
      #  s.set_pixel(x, y, imMenu[y])
      if y > 0:
        y = y - 1
    #print(mode, x, y, newCol)

def s_left(event):
  global x, mode
  
  #print('left')
  #print(event.action)
  if event.action != ACTION_RELEASED:
    if mode == 'menu':
      mode = 'edit'
      flash_stop = True
      display(im, mode)
    elif mode == 'edit':
      #s.set_pixel(x, y, im[x + y * 8])
      if x > 0:
        x = x - 1
    elif mode == 'show':
      # leave the show without loading
      mode = 'menu'
      display(im, mode)
    #print(mode, x, y, newCol)

def s_right(event):
  global x, mode
  
  #print('right')
  #print(event.action)
  if event.action != ACTION_RELEASED:
    if x == 7:
      if mode == 'edit':
        mode = 'menu'
        flash_stop = True
        display(im, mode)
##      elif mode == 'menu':
##        mode = 'show'
##        imGal = [nothing] * 64
##        load_gallery()
##        if len(gallery) == 0:
##          imGal = [nothing] * 64
##        else
##          imGal = gallery[lot]
##        display(imGal, mode)
##      elif mode == 'show':
##        pass
    else:
      s.set_pixel(x, y, im[x + y * 8])
      x = x + 1
    #print(mode, x, y, newCol)

def s_middle(event):
  global newCol, im, mode, lot
  
  #print('middle')
  #print(event.action)
  if event.action != ACTION_RELEASED:
    if mode == 'edit':
      #print('paint', x, y, newCol)
      im[x + y * 8] = newCol
      s.set_pixel(x, y, newCol)
    elif mode == 'menu':
      if y == 0: #new
        #print('new')
        im = [nothing] * 64
        display(im, mode)
      elif y == 1: #save
        #print('save')
        #print(im)
        append_gallery(im)
        s.show_letter('+', text_colour = [0, 255, 0])
        time.sleep(1)
        #else:
        #  s.show_letter('X', text_colour = [255, 0, 0])
        display(im, mode)
      elif y == 2: #load
        #print('load')
        if load_gallery():
          if gallery_depth == 1:
            # only one image in the gallery
            lot = 0
            imGal = gallery
          else: # show first picture
            lot = 0
            imGal = gallery[0]
          mode = 'show'
          #print(mode, imGal)
          flash_stop = True
          display(imGal, mode)  
      elif y > 2:
        newCol =  imMenu[y]
    elif mode == 'show':
      mode = 'menu'
      if gallery_depth == 1:
        # only one image in the gallery
        im = gallery
      else: # load picture of #lot
        im = gallery[lot]
      display(im, mode)
    #print(mode, x, y, newCol)

def s_any(event):
  #print('any')
  #print(event.direction, event.action)
  #print(mode, x, y, newCol)
  pass


def main():
  global im
  h_old = int(s.get_humidity())
  an_old = acc_neg_count(s.get_accelerometer_raw())
  fade()
  
  im = [nothing] * 64
  display(im, mode)
  
  #print(mode, x, y, newCol)
  
  # set up call back functions
  s.stick.direction_down = s_down
  s.stick.direction_left = s_left
  s.stick.direction_right = s_right
  s.stick.direction_up = s_up
  
  s.stick.direction_middle = s_middle

  s.stick.direction_any = s_any

  while True:
    # flash the current pixel
    flash(x, y)
    
    h = int(s.get_humidity()) # Take humidity reading
    if h > (h_old + 3): # If humidity has increased...
      #print('smelly breath', h_old, h)
      fade()
    else:
      h_old = h

    # check only for large movements
    # by comparing sign of movement from accelerometer
    an = acc_neg_count(s.get_accelerometer_raw())
    if an != an_old:
      #print('shuffle bottom', an_old, an)
      bright()
      an = an_old

    
try:
  main()
except KeyboardInterrupt:
  pass
finally:
  if not s is None:
    s.clear()
