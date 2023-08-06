#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 12:58:40 2018

@author: andrew
"""

import glob
import os
from pyraf import iraf
from initialize import loc

#%%
#makes or updates list of all fits images in a directory
def inputlist(location):
    x = 0
    file = open("%s/inputs.txt" % (location), "w+")
    images = glob.glob(location + "/*_N_.fits")
    ref = glob.glob(location + "/*_ref_A_.fits")
    if len(ref) == 1:
        file.write(str(ref[0]) + "\n")
        x += 1
    else:
        print("problem with reference image")
    for i in images:
        file.write(i + "\n")
        x += 1
    file.close()
    print("input list updated for %s (%d images)" % (location, x))
    
#%%
#makes or updates list of all ouput names of fits files in a directory
def outputlist(location):
    x = 0
    file = open("%s/outputs.txt" % (location), "w+")
    images = glob.glob(location + "/*_N_.fits")
    ref = glob.glob(location + "/*_ref_A_.fits")
    if len(ref) == 1:
        file.write(str(ref[0]) + "\n")
        x += 1
    else:
        print("problem with reference image")
    for i in images:
        i = i[:-8]
        file.write(i + "_A_.fits" + "\n")
        x += 1
    file.close()
    print("output list updated for %s (%d images)" % (location, x))
    
#%%
#aligns images in a directory using IRAF imalign
def align(location):
    inputlist(location)
    outputlist(location)
    ref_image = glob.glob(location + "/*_ref_A_.fits")
    input_list = glob.glob(location + "/inputs*")
    output_list = glob.glob(location + "/outputs*")
    coordinates = glob.glob(location + "/*.coo")
    if input_list == []:
        print("no input list found")
    elif output_list == []:
        print("no output list found")
    elif coordinates == []:
        print("no coordinate list found")
    elif ref_image == []:
        print("no reference image found")
    elif len(input_list) > 1:
        print("too many input lists")
    elif len(output_list) > 1:
        print("too many ouptut lists")
    elif len(coordinates) > 1:
        print("too many coordinate lists")
    elif len(ref_image) > 1:
        print("too many reference images")
    else:
        try:
            ref_image = ref_image[0]
            input_list = "@" + input_list[0]
            output_list = "@" + output_list[0]
            coordinates = coordinates[0]
            iraf.imalign(input=input_list, reference=ref_image, coords=coordinates, output=output_list, boxsize = 20, bigbox = 30)
            images = glob.glob(location + "/*_N_.fits")
            for i in images:
                os.system("mv %s %s/sdi/archive/data" % (i, loc))
            print("alignment successful!")
            print("moved non-aligned _N_ images to sdi archive")
        except iraf.IrafError:
            print("alignment failed, check parameters")