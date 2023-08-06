#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 12:59:46 2018

@author: andrew
"""

import glob
import astroalign
from astropy.io import fits
import numpy as np

#%%
#align aligned images to template using astroalign package
def align3(location):
    x = 1
    images = glob.glob(location + "/data/*_A_.fits")
    temp = glob.glob(location + "/templates/*.fits")
    hdu2 = fits.open(temp[0])
    data2 = hdu2[0].data
    data2 = np.array(data2, dtype="float64")  
    for i in images:
        hdu1 = fits.open(i)
        data1 = hdu1[0].data
        data1 = np.array(data1, dtype="float64")
        aligned = astroalign.register(data1, data2)
        aligned_name = i[:-8] + "_AT_.fits"
        hdu = fits.PrimaryHDU(aligned, header=hdu1[0].header)
        hdu.writeto(aligned_name)
        hdu1.close()
        percent = float(x)/float(len(images)) * 100
        print "%.3f%% aligned..." % (percent)
        x += 1
    hdu2.close()