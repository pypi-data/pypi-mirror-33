#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 12:54:19 2018

@author: andrew
"""

import os
import zipfile
from astropy.io import fits
import glob
from initialize import loc
from initialize import create

#%%
#move downloaded LCO data from download_loc to temp folder
def move(download_loc):
    temp = "%s/sdi/temp" % (loc)
    num = 1
    x = []
    y = []
    for root, dirs, files in os.walk(download_loc):
        for f in files:
            if f[:3] == "lco":
                os.system('mv "%s/%s" %s' % (download_loc, f, temp))
                x.append(num)
        for d in dirs:
            if d[:3] == "lco":
                os.system('mv "%s/%s" %s' % (download_loc, d, temp))
                y.append(num)
    print("moved %d files and %d directories from %s to /sdi/temp\n" % (sum(x), sum(y), download_loc))
    
#%%
#unzips and funpacks downloaded LCO data in temp directory
def process():
    num = 1
    x = []
    y = []
    d = 0
    temp = "%s/sdi/temp" % (loc)
    zipfiles = glob.glob("%s/*.zip" % (temp))
    for i in zipfiles:
        zip_ref = zipfile.ZipFile(i, 'r')
        zip_ref.extractall(temp)
        zip_ref.close()
        os.remove(i)
        x.append(num)
        d =+ 1
    for d in os.listdir(temp):
        if os.path.isdir(temp+"/"+d)==True:
            for j in os.listdir(temp+"/"+d):
                if j.endswith(".fz"):
                    os.system('funpack "%s/%s/%s"' % (temp, d, j))
                    os.system('rm "%s/%s/%s"' % (temp, d, j))
                    y.append(num)
    print("%d files unzipped and %d images funpacked\n" % (sum(x), sum(y)))
    
#%%
#moves data from /sdi/temp to its respective target directory
def movetar(tar):
    check = os.path.exists("%s/sdi/targets/%s" % (loc, tar))
    if check == False:
        os.system("mkdir %s/sdi/targets/%s" % (loc, tar))
        os.system("mkdir %s/sdi/targets/%s/raw_data" % (loc, tar))
    one = 1
    x = []
    y = []
    temp = "%s/sdi/temp" % (loc)
    data = "%s/sdi/targets/%s" % (loc, tar)
    raw_data = "%s/sdi/targets/%s/raw_data" % (loc, tar)
    for d in os.listdir(temp):
        files = glob.glob(temp + "/" + d + "/*.fits")
        for f in files:
            if f[-7] == "9":
                os.system("mv %s %s" % (f, data))
                x.append(one)
            if f[-7] == "0" or f[-7] == "1":
                os.system("mv '%s' %s" % (f, raw_data))
                y.append(one)
        try:
            if os.listdir(temp + "/" + d) == []:
                os.rmdir(temp + "/" + d)
                print("removed %s because it became empty\n" % (d))
        except NotADirectoryError:
            pass
    print("moved %d images to %s\n" % (sum(x), data))
    print("moved %d raw images to %s\n" % (sum(y), raw_data))
    if check == False:
        print("created %s directory in %s/sdi/targets\n" (tar, loc))
        
#%%
#group images of same RA and DEC together in their own directories
def rename(tar):
    x = []
    one = 1
    target = "%s/sdi/targets/%s" % (loc, tar)
    length = len(target) + 1
    for f in glob.glob("%s/*.fits" % (target)):
        F = f[length:]
        hdu = fits.open(f)
        ra = hdu[0].header['CAT-RA']
        dec = hdu[0].header['CAT-DEC']
        fltr = hdu[0].header['FILTER1']
        exp = round(int(hdu[0].header['EXPTIME']))
        stoptime = hdu[0].header['UTSTOP']
        check = os.path.exists("%s/%s_%s" % (target, ra, dec))
        if check == False:
            os.system("mkdir %s/%s_%s" % (target, ra, dec))
            os.system("mkdir %s/%s_%s/%s" % (target, ra, dec, fltr))
            os.system("mkdir %s/%s_%s/%s/%s" % (target, ra, dec, fltr, exp))
            create("%s/%s_%s/%s/%s" % (target, ra, dec, fltr, exp))
            os.system("mv %s %s/%s_%s/%s/%s/data" % (f, target, ra, dec, fltr, exp))
            os.system("mv %s/%s_%s/%s/%s/data/%s %s/%s_%s/%s/%s/data/%s_N_.fits" % (target, ra, dec, fltr, exp, F, target, ra, dec, fltr, exp, stoptime))
        if check == True:
            check2 = os.path.exists("%s/%s_%s/%s" % (target, ra, dec, fltr))
            if check2 == False:
                os.system("mkdir %s/%s_%s/%s" % (target, ra, dec, fltr))
                os.system("mkdir %s/%s_%s/%s/%s" % (target, ra, dec, fltr, exp))
                create("%s/%s_%s/%s/%s" % (target, ra, dec, fltr, exp))
                os.system("mv %s %s/%s_%s/%s/%s/data" % (f, target, ra, dec, fltr, exp))
                os.system("mv %s/%s_%s/%s/%s/data/%s %s/%s_%s/%s/%s/data/%s_N_.fits" % (target, ra, dec, fltr, exp, F, target, ra, dec, fltr, exp, stoptime))
            if check2 == True:
                check3 = os.path.exists("%s/%s_%s/%s/%s" % (target, ra, dec, fltr, exp))
                if check3 == False:
                    os.system("mkdir %s/%s_%s/%s/%s" % (target, ra, dec, fltr, exp))
                    create("%s/%s_%s/%s/%s" % (target, ra, dec, fltr, exp))
                    os.system("mv %s %s/%s_%s/%s/%s/data" % (f, target, ra, dec, fltr, exp))
                    os.system("mv %s/%s_%s/%s/%s/data/%s %s/%s_%s/%s/%s/data/%s_N_.fits" % (target, ra, dec, fltr, exp, F, target, ra, dec, fltr, exp, stoptime))
                if check3 == True:
                    os.system("mv %s %s/%s_%s/%s/%s/data" % (f, target, ra, dec, fltr, exp))
                    os.system("mv %s/%s_%s/%s/%s/data/%s %s/%s_%s/%s/%s/data/%s_N_.fits" % (target, ra, dec, fltr, exp, F, target, ra, dec, fltr, exp, stoptime))
        x.append(one)
        hdu.close()
    print("%d images grouped into location directories\n" % (sum(x)))
    