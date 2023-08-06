#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 13:00:21 2018

@author: andrew
"""

from time import strftime
from time import gmtime
import glob
from initialize import loc
from pyraf import iraf
import os

#%%
#combine all aligned images in a directory to make a template and move template to template directory
def combine(location, method = "median"):
    location = location[:-5]
    time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    images = glob.glob(location + "/data" + "/*_A_.fits")
    og_templates = glob.glob(location + "/templates/*.fits")
    ref = glob.glob(location + "/data" + "/*_ref_.fits")
    log_loc = location + "/templates/log.txt"
    tlist_loc = location + "/templates/template_inputs.txt"
    log_list = open(log_loc, "a+")
    template_list = open(tlist_loc, "w+")
    for i in images:
        template_list.write(str(i) + "\n")
    template_list.close()
    if images == []:
        print("no aligned images to combine\n")
    else:
        output_image = log_loc[:-7] + str(len(images)) + "_" + method + ".fits"
        try:
            print("images being combined...\n")
            iraf.imcombine(input="@" + tlist_loc, output=output_image, combine=method)
            log_list.write("template updated at %s UTC | method = %s (IRAF) | images = %d\n" % (str(time), method, len(images)))
            log_list.close()
            if len(og_templates) > 0:
                for o in og_templates:
                    os.system("mv %s %s/sdi/archive/templates" % (o, loc))
            print("image combination successful!\ntemplate log updated\n")
        except:
            print("image combination failed\n")