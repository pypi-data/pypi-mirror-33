#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 10:28:32 2018

@author: andrew
"""

import glob
import numpy as np
from astropy.io import fits
import os
from initialize import loc

#%%
#checks all fits images in a directory for saturation
def check_saturate(location):
    print("checking images for saturation...")
    Max = []
    im = []
    m = []
    x = 0
    y = 0
    z = 0
    images = glob.glob(location + "/*.fits")
    length = len(location) + 6
    for i in images:
        hdu = fits.open(i)
        lin = hdu[0].header['MAXLIN']
        data = hdu[0].data
#        rows = np.size(data, axis=0)
#        cols = np.size(data, axis=1)
#        for r in np.arange(rows):
#            for c in np.arange(cols):
#                if data[r, c] > lin:
#                    x += 1
        sat = ((data>lin)).sum()
#        ind = np.unravel_index(np.argmax(data, axis=None), data.shape)
#        excess = data[ind[0], ind[1]] - lin
        if sat > 3:
#            print "\n%s saturated | # saturated pixels = %d | max pixel location = (%d, %d)\nmax value over linearity limit = %d" % (i[length:], x, ind[0], ind[1], excess)
            y += 1
            im.append(i)
            m.append(np.max(data))
        Max.append(np.max(data))
#        x = 0
        sat = 0
        hdu.close()
    if y > 0:
        print("\n%d/%d saturated images" % (y, len(images)))
        print("\naverage saturation level (ADU) = %d" % (np.mean(m)-lin))
        return im
    if y == 0:
        diff = lin - np.max(Max)
        print("\nno saturated images in %s" % (location))
        print("\nclosest value to saturation = %d" % (np.max(Max)))
        print("\ndifference between this value and saturation level = %d" % (diff))
        return y
    
#%%
#move images into archives
def move_arch(images):
    archive_data_loc = loc + "/sdi/archive/data"
    for i in images:
        os.system("mv %s %s" % (i, archive_data_loc))
    print("Saturated images moved to SDI archives")