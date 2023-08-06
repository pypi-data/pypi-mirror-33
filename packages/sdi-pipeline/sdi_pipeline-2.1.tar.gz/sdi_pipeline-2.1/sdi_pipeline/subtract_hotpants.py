#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 13:04:11 2018

@author: andrew
"""

import glob
import os

#%%
#subtract using hotpants
def hotpants(location):
    x = 0
    images = glob.glob(location + "/data/*_A_.fits")
    template = glob.glob(location + "/templates/*.fits")
    outputs = []
    length = len(location) + 6
    if len(template) == 1:
        for i in images:
            outputs.append(location + "/residuals/" + i[length:-8] + "_hotpants.fits")
            os.system("./hotpants -inim %s -tmplim %s -outim %s" % (images[x], template[0], outputs[x]))
            x += 1
            per = float(x)/float(len(images)) * 100
            print("%d subtracted..." % (per))
    else:
        print("error with number of templates")