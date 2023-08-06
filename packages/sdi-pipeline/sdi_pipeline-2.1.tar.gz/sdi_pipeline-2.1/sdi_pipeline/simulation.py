#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May  2 15:45:30 2018

@author: andrew
"""
import random
import os
import glob
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
import shutil
from initialize import loc

#%%
#make a copy of target directory in the simulations directory
def copy_to_sim(tar):
    sim_path = loc + "/sdi/simulations"
    tar_dir_path = loc + "/sdi/targets"
    try:
        shutil.copytree(tar_dir_path + "/" + tar, sim_path + "/" + tar)
        print("Copy target directory created in simulations directory")
    except Exception as e:
        print(e)
        
#%%
#create fakes directory for a given target
def fake_dir(location):
    fake_dir = location + "/fakes"
    if os.path.exists(fake_dir) == False:
        os.mkdir(fake_dir)
    else:
        print("Fakes directory already exists for this target")

#%%
def fakes(location, mag):
    fakes = location + "/fakes"
#    clear contents of directory
    for i in os.listdir(fakes):
        path = os.path.join(fakes, i)
        try:
            if os.path.isfile(path):
                os.unlink(path)
        except Exception as e:
            print(e)
    FAKE = glob.glob(location +"/data/*FAKE.fits")
    if FAKE != []:
        for i in FAKE:
            os.system("rm %s" % (i))
    fake_res = glob.glob(location + "/residuals/*FAKE_residual.fits")
    if fake_res != []:
        for i in fake_res:
            os.system("rm %s" % (i))
    catalogs = glob.glob(location + "/sources/*.cat")
    if catalogs != []:
        for i in catalogs:
            os.system("rm %s" % (i))
#    create skymaker catalog
    cat = open(fakes + "/sky.cat", "w+")
    config = "/home/andrew/sdi/pipeline/scripts/sky.config"
    data = []
    x = random.randint(0,1526)
    y = random.randint(0,1017)
#    mag = random.uniform(12,20)
    data.append("100" + "   " + str(x) + "   " + str(y) + "   " + str(mag) + "\n")
    for i in data:
        cat.write(i)
    cat.close()
    name = "%s/fakes/%d_%d_%.3f_sky.fits" % (location,x,y,mag)
    with open(config, 'r') as Config:
        data = Config.readlines()
        Config.close()
    data[6] = "IMAGE_NAME" + "        " + name + "\n"
    with open(config, 'w') as Config:
        Config.writelines(data)
        Config.close()
    os.system("sky -c %s %s/fakes/sky.cat" % (config, location))
    images = glob.glob(location + "/data/*_A_.fits")
    fake = glob.glob(location + "/fakes/*.fits")
    comb_name = location + "/data/%d_%d_%.3f_FAKE.fits" % (x,y,mag)
    num = len(images) - 1
    im = random.randint(0,num)
    hdu1 = fits.open(images[im])
    data1 = hdu1[0].data
    Header = hdu1[0].header
    hdu2 = fits.open(fake[0])
    data2 = hdu2[0].data
    comb = data1+data2
    hdu3 = fits.PrimaryHDU(comb, header=Header)
    hdu3.writeto(comb_name)
#    print images[im]
    template = glob.glob(location + "/templates/*.fits")
    fake = glob.glob(location + "/data/*FAKE.fits")
    sub_name = location + "/residuals/FAKE_residual.fits"
    hdu4 = fits.open(template[0])
    data4 = hdu4[0].data
    hdu5 = fits.open(fake[0])
    data5 = hdu5[0].data
    sub = data5 - data4
    hdu6 = fits.PrimaryHDU(sub)
    hdu6.writeto(sub_name)
    combine2(location + "/residuals")
    sex_config = "/home/andrew/sdi/pipeline/scripts/fakesex_config"
    sex_param = "/home/andrew/sdi/pipeline/scripts/fakesex_param"
    fake = glob.glob(location + "/data/*FAKE.fits")
    length = len(location) + 6
    catalog_name = location + "/sources/" + str(fake[0][length:-9]) + ".cat"
    combined_res = glob.glob(location + "/residuals/*COMBINED_residual.fits")
    with open(sex_config, 'r') as Config:
        data = Config.readlines()
        Config.close()
    data[6] = "CATALOG_NAME" + "        " + catalog_name + "\n"
    with open(sex_config, 'w') as Config:
        Config.writelines(data)
        Config.close()
    os.system("sextractor -c %s %s" % (sex_config, combined_res[0]))
    X,Y = sex_cat(location)
    x_high = x+1
    x_low = x-1
    y_high = y+1
    y_low = y-1
    detections = []
    for i in range(len(X)):
        if float(X[i]) >= x_low and float(X[i]) <= x_high and float(Y[i]) >= y_low and float(Y[i]) <= y_high:
            detections.append(i)
    distance_from_core = np.sqrt((754-x)**2+(487-y)**2)
    return detections

#%%
def combine2(location):
    combined = glob.glob(location + "/*COMBINED_residual.fits")
    if combined != []:
        for i in combined:
            os.system("rm %s" % (i))
    data = []
    images = glob.glob(location + "/*.fits") 
    for i in images:
        hdu1 = fits.open(i)
        data1 = hdu1[0].data
        data1 = np.array(data1, dtype="float64")
        data.append(data1)
        Header = hdu1[0].header
        hdu1.close()
    comb = sum(data)
    combined_name = location + "/COMBINED_residual.fits"
    hdu = fits.PrimaryHDU(comb, header=Header)
    hdu.writeto(combined_name)
    
def fake_sub(location):
    fake_res = glob.glob(location + "/residuals/*FAKE_residual.fits")
    if fake_res != []:
        for i in fake_res:
            os.system("rm %s" % (i))
    template = glob.glob(location + "/templates/*.fits")
    fake = glob.glob(location + "/data/*FAKE.fits")
    sub_name = location + "/residuals/FAKE_residual.fits"
    hdu1 = fits.open(template[0])
    data1 = hdu1[0].data
    hdu2 = fits.open(fake[0])
    data2 = hdu2[0].data
    sub = data2 - data1
    hdu3 = fits.PrimaryHDU(sub)
    hdu3.writeto(sub_name)
    combine2(location + "/residuals")
    
def fake_sex(location, target):
    catalogs = glob.glob(location + "/sources/*.cat")
    if catalogs != []:
        for i in catalogs:
            os.system("rm %s" % (i))
    sex_config = "/home/andrew/sdi/pipeline/scripts/fakesex_config"
    sex_param = "/home/andrew/sdi/pipeline/scripts/fakesex_param"
#    fake = glob.glob(location + "/data/*FAKE.fits")
    length = len(location) + 6
    catalog_name = location + "/sources/" + target + ".cat"
    combined_res = glob.glob(location + "/residuals/*COMBINED_residual.fits")
    with open(sex_config, 'r') as Config:
        data = Config.readlines()
        Config.close()
    data[6] = "CATALOG_NAME" + "        " + catalog_name + "\n"
    with open(sex_config, 'w') as Config:
        Config.writelines(data)
        Config.close()
    os.system("sextractor -c %s %s" % (sex_config, combined_res[0]))
    
def sex_cat(location):
    q = 0
    p = 0
    r = 0
    indeces = []
    x = []
    y = []
    class_star = []
    catalog = glob.glob(location + "/sources/*.cat")
    with open(catalog[0], 'r') as cat:
        lines = cat.readlines()
        cat.close()
    for i in lines:
        b = i.split(" ")
        b[:] = [j for j in b if j != '']
        b[:] = b[:3]
        if b[0] != '#':
            r += 1
            x.append(b[0])
            y.append(b[1])
            class_star.append(b[2])
            if float(b[2]) < 0.09:
                indeces.append(q)
            else:
                p += 1
        q += 1
    for j in indeces:
        lines[j] = "#" + "   " + lines[j]
    with open(catalog[0], 'w+') as cat:
        cat.writelines(lines)
        cat.close()
    print "sources = %d | detections = %d" % (r, p)

#P = 0
#D = []
#mag = []
#for i in np.arange(12,22,0.2):
#    for j in range(50):
#        det = fakes("/home/andrew/sdi/simulations/NGC6744/20.0", i)
#        D.append(det)
#        mag.append(i)
#    P += 1
#    print "%.2f%%" % (P/50.0*100)
#    
#for i in range(len(D)):
#    if D[i] == []:
#        D[i] = 0
#    else:
#        D[i] = 1
#    
#detect = []
#for i in range(50):
#    p = 50 + (50*i)
#    q = 0
#    l = i - 1
#    if l >= 0:
#        q = 50 + (50*l)
#    X = D[q:p]
#    detect.append(sum(X)/50.0)

#M = []
#for i in np.arange(12,22,0.2):
#    M.append(i)

#D_M_NGC6744 = []
#for i in detect:
#    D_M_NGC6744.append(i)
    
#M_NGC6744 = []
#for i in M:
#    M_NGC6744.append(i)
    
A, = plt.plot(D_NGC2403, D_D_NGC6744, label='NGC 6744')
B, = plt.plot(D_NGC2403, D_D_NGC3031, label='NGC 3031')
C, = plt.plot(D_NGC2403, D_D_NGC2403, label='NGC 2403')
D, = plt.plot(D_NGC2403, Y, '--',label='core distance threshold')
plt.xlabel('distance to core (arcseconds)')
plt.ylabel('$N_det / N_tot$')
first_legend = plt.legend(handles=[A,B,C])
ax = plt.gca().add_artist(first_legend)
plt.legend(handles=[D], loc=3)
plt.ylim([0,1.4])
plt.show()