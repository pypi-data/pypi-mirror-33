#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 13:04:32 2018

@author: andrew
"""

import os
import glob

#%%
#runs SExtractor on all residual images in a directory
def sex(location):
    x = 0
    sources = location + "/sources"
    residuals = location + "/residuals"
    check = os.path.exists(sources)
    length = len(residuals) + 1
    if check == False:
        os.system("mkdir %s" % (sources))
    images = glob.glob(residuals + "/*.fits")
    for i in images:
        name = i[length:-5]
        os.system("sextractor %s > %s/%s.txt" % (i, sources, name))
        x += 1
        per = float(x)/float(len(images)) * 100
        print("%d sextracted..." % (per))
    print("SExtracted %d images, catalogues places in 'sources' directory\n" % (len(images)))
