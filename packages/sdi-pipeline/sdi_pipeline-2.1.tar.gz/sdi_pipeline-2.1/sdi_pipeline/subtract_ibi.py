#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 13:02:21 2018

@author: andrew
"""

import glob
import copy
from astropy.io import fits
import numpy as np

#%%
def subtract3(location):
    y = 0
    images = glob.glob(location + "/data/*_A_.fits")
    images_copy = copy.deepcopy(images)
    length = len(location) + 6
    for i in images:
        hdu1 = fits.open(i)
        data1 = hdu1[0].data
        data1 = np.array(data1, dtype="float64")
        images_copy.remove(i)
        y += 1
        for j in images_copy:
            hdu2 = fits.open(j)
            data2 = hdu2[0].data
            data2 = np.array(data2, dtype="float64")
            sub = data1 - data2
            sub_name = location + "/residuals/" + j[length:-5] + "residual%d.fits" % (y)
            hdu = fits.PrimaryHDU(sub, header=hdu2[0].header)
            hdu.writeto(sub_name)
            hdu1.close()
        hdu1.close()
    print("image subtraction successful")