#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 13:00:46 2018

@author: andrew
"""

import glob
from time import strftime
from time import gmtime
import numpy as np
from astropy.io import fits

#%%
#combine all aligned images in data directory to make a template using the median method and move the temp to the templates dir
def combine_median(location):
    location = location[:-5]
    data = []
    images = glob.glob(location + "/data" + "/*_A_.fits")
    log_loc = location + "/templates/log.txt"
    log_list = open(log_loc, "a+")
    time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    for i in images:
        hdu1 = fits.open(i)
        data1 = hdu1[0].data
        data1 = np.array(data1, dtype="float64")
        data.append(data1)
        Header = hdu1[0].header
        hdu1.close()
    comb = np.median(data, axis=0)
    combined_name = location + "/templates/median_%d.fits" % (len(images))
    hdu = fits.PrimaryHDU(comb, header=Header)
    hdu.writeto(combined_name)
    log_list.write("template updated at %s UTC | method = median (numpy) | images = %d\n" % (str(time), len(images)))
    log_list.close()
    print("image combination successful!\ntemplate log updated\n")
    return comb