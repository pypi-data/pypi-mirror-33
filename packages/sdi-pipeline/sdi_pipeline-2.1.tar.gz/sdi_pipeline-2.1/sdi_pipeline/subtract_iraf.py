#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 13:01:41 2018

@author: andrew
"""

import glob
from pyraf import iraf

#%%
#subtracts an image or group of images from a specified template image
def subtract(location):
    tlist_loc = location + "/templates/template_inputs.txt"
    template_loc = glob.glob(location + "/templates/*.fits")
    res_outputs = open(location + "/residuals/residual_outputs.txt", "w+")
    res_outputs_loc = location + "/residuals/residual_outputs.txt"
    images = glob.glob(location + "/data" + "/*_A_.fits")
    length = len(location) + 6
    for i in images:
        res_outputs.write(location + "/residuals/" + i[length:-5] + "residual.fits\n")
    res_outputs.close()
    if len(template_loc) == 1:
        try:
            iraf.imarith(operand1="@" + str(tlist_loc), op="-", operand2=str(template_loc[0]), result="@" + str(res_outputs_loc))
            print("image subtraction successful")
        except:
            print("subtraction failed")
    else:
        print("problem with template image")