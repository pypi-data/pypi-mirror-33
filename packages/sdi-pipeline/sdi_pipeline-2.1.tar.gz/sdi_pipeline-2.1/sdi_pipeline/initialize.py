from os.path import expanduser
import os

loc = expanduser("~")

#%%
#run on a new computer to create the sdi file system and use the pipeline
def initialize(loc):
    if os.path.exists(loc + "/sdi") == False:
        os.system("mkdir %s/sdi" % (loc))
        os.system("mkdir %s/sdi/targets" % (loc))
        os.system("mkdir %s/sdi/temp" % (loc))
        os.system("mkdir %s/sdi/sources" % (loc))
        os.system("mkdir %s/sdi/archive" % (loc))
        os.system("mkdir %s/sdi/pipeline" % (loc))
        os.system("mkdir %s/sdi/observations" % (loc))
        os.system("mkdir %s/sdi/simulations" % (loc))
        os.system("mkdir %s/sdi/archive/data" % (loc))
        os.system("mkdir %s/sdi/archive/templates" % (loc))
        os.system("mkdir %s/sdi/archive/residuals" % (loc))
        os.system("mkdir %s/sdi/scripts" % (loc))
        print("sdi file system created in %s\n" % (loc))
    else:
        print("SDI architecure already exists on this computer")
    
#%%
#creates a data, template, and residual directory
def create(location):
    dirs = ["data", "templates", "residuals", "sources", "psf"]
    for d in dirs: os.system("mkdir %s/%s" % (location, d))
    print("data, templates, residuals, sources, and psf directories created in %s\n" % (location))

#%%
#if this architecture does not exist, create it
if __name__ == '__main__':
    alert = input("Create SDI directories in %s? (y/n)\n" % (loc))
    if alert == 'y':
        initialize(loc)
    elif alert == 'n':
        print("Change loc variable in initialize.py to desired SDI directory path, then run script again")
    else:
        print("Error: unknown input")