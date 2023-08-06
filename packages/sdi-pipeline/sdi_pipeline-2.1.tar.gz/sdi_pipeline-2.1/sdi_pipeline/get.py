import obtain
from initialize import loc
from initialize import create

if __name__ == '__main__':
    download_location = input("Enter LCO data location (leave blank for default=%s/Downloads): " % (loc))
    if download_location == "":
        download_location = "%s/Downloads" % (loc)
    obtain.move(download_location)
    obtain.process()
    check = input("Move data into target directory? (y/n): ")
    if check == "y":
        tar = input("Enter target: ")
        obtain.movetar(tar)
        obtain.rename(tar)
    elif check != "y" and check != "n":
        print("Error: unknown Input")