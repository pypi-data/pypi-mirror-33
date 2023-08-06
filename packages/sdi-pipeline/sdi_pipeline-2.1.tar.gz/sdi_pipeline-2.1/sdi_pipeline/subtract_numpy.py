#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 13:02:02 2018

@author: andrew
"""

import glob
from astropy.io import fits
import numpy as np

#%%
def subtract2(location):
    length = len(location) + 6
    images = glob.glob(location + "/data/*_A_.fits")
    template = glob.glob(location + "/templates/*.fits")
    hdu1 = fits.open(template[0])
    data1 = hdu1[0].data
    data1 = np.array(data1, dtype="float64")  
#    data1 = data1[:-1]
    for i in images:
        hdu2 = fits.open(i)
        data2 = hdu2[0].data
        data2 = np.array(data2, dtype="float64")
        sub = data2 - data1
        sub_name = location + "/residuals/" + i[length:-5] + "residual.fits"
        hdu = fits.PrimaryHDU(sub, header=hdu2[0].header)
        hdu.writeto(sub_name)
        hdu2.close()
    hdu1.close()
    print("image subtraction successful")