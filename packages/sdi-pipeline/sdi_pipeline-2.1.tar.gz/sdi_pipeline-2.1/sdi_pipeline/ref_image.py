#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 12:58:10 2018

@author: andrew
"""

import glob
import numpy as np
from astropy.io import fits
import os

#%%
#rename first image in directory to be the reference image
def ref_image(location):
    noise = []
    ref = glob.glob(location + "/*_ref_A_.fits")
    length = len(location) + 1
    if ref == []:
        images = glob.glob(location + "/*.fits")
        for i in images:
            hdu = fits.open(i)
            data = hdu[0].data
            noise.append(np.mean(data))
        im = images[np.argmin(noise)]
        reference = location + "/" + im[length:-8] + "_ref_A_.fits"
        os.system("mv %s %s" % (im, reference))
        print("designated %s as the reference image in this directory\n" % (im))
    else:
        print("reference image already exists in this directory\n")