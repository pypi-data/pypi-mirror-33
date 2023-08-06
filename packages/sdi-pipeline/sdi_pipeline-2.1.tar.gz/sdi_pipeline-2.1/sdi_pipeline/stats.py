#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 13:08:34 2018

@author: andrew
"""

#%%
#gives statistics of all iamges in a directory
def stats(location):
    images = glob.glob(location + "/*.fits")
    means = []
    stdev = []
    for i in images:
        hdu = fits.open(i)
        data = hdu[0].data
        means.append(np.mean(data))
        stdev.append(np.std(data))
        hdu.close()
    mean = np.mean(means)
    std = np.mean(stdev)
    print "Average image background value = %d | Average standard deviation = %d" % (mean, std)

#%%
#get statistics and plots for a single pixel value across many images
def pixel_stats(location, i, j):
    import matplotlib.pyplot as plt
    x = 0
    images = glob.glob(location + '/data/*.fits')
    pixel = []
    for im in images:
        hdu = fits.open(im)
        data = hdu[0].data
        site = hdu[0].header['SITE']
        pixel.append(data[i, j])
        hdu.close()
        if data[i, j] < 300:
            os.system("rm %s" % (im))
            x += 1
    samples = len(pixel)
    Max = np.max(pixel)
    Min = np.min(pixel)
    mean = np.mean(pixel)
    median = np.median(pixel)
    stdev = np.std(pixel)
    threesig_up = mean + 3*stdev
    threesig_down = mean - 3*stdev
    twosig_up = mean + 2*stdev
    twosig_down = mean - 2*stdev   
    plt.hist(pixel, bins=15, rwidth=0.7)
    plt.title("Pixel Values (%d, %d) [%d samples]" % (i, j, samples))
    if Max < threesig_up and Min > threesig_down:
        if Max < twosig_up and Min > twosig_down:
            print "all pixels contained within 2 sigma"
        else:
            print "all pixels contained within 3 sigma"
    else:
        print "pixels exceed 3 sigma"
    print "max = %d\nmin = %d\nmean = %d\nmedian = %d\nstdev = %d" % (Max, Min, mean, median, stdev)
    print x
    
#%%
#get statistics and plots for a group of images
def image_stats(location):
    x = 0
    images = glob.glob(location + '/*.fits')
    sums = []
    means = []
    stdev = []
    Max = []
    Min = []
    median = []
    for im in images:
        hdu = fits.open(im)
        array = hdu[0].data
        array = array[387:550, 700:850]
#        molnum = hdu[0].header['MOLNUM']
#        siteid = hdu[0].header['SITEID']
        sums.append(np.sum(array))
        stdev.append(np.std(array))
        Max.append(np.max(array))
        Min.append(np.min(array))
        median.append(np.median(array))
#        print np.mean(array)
#        x += 1
#        means.append(np.mean(array))
        if np.mean(array) < 375 and np.mean(array) > 330:
            x += 1
            print im
            means.append(np.mean(array))
            os.system("cp %s /home/andrew/images2/data" % (im))
#        threesig_up = np.mean(array) + 3*np.std(array)
#        threesig_down = np.mean(array) - 3*np.std(array)
#        twosig_up = np.mean(array) + 2*np.std(array)
#        twosig_down = np.mean(array) - 2*np.std(array)
#        if np.max(array) < threesig_up and np.min(array) > threesig_down:
#            if Max < twosig_up and Min > twosig_down:
#                print "all pixels contained within 2 sigma"
#            else:
#                print "all pixels contained within 3 sigma"
#        else:
#            print "pixels exceed 3 sigma"
#        hdu.close()
#    samples = len(images)
#    plt.hist(sums, bins = 20, rwidth = 0.7)
#    plt.title("Sum Image Values [%d samples]" % (samples))
#    plt.figure()
    plt.hist(means, bins = 100, rwidth = 0.7)
#    plt.title("Mean Residual Values (ADU) [%d M31 Off-Core frames]" % (samples))
    plt.figure()
#    plt.hist(stdev, bins = 20, rwidth = 0.7)
#    plt.title("Standard Deviations (ADU) [%d M31 Off-Core frames]" % (samples))
#    plt.figure()
#    print "mean = %d" % (float(np.mean(means)))
    #print "max = %d\nmin = %d\nmean = %d\nmedian = %d\nstdev = %d" % (Max, Min, mean, median, stdev)
#    for i in range(len(sums)):
#        sums[i] *= 10**-6
#    plt.figure()
#    plt.imshow(array, cmap='gray')
#    plt.figure()
    print x
    print images[np.argmin(means)], images[np.argmax(means)]
    return np.std(means), np.mean(means), np.median(sums), array
    