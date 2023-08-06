from initialize import loc
import subtract_hotpants
import subtract_ibi
import subtract_numpy

if __name__ == '__main__':
    path = input("Enter path to exposure time directory: ")
    method = input("Choose subtraction method: numpy (default), hotpants, image-by-image, or iraf: ")
    if method == 'numpy' or method == '':
        subtract_numpy.subtract2(path)
    elif method == 'hotpants':
        subtract_hotpants.hotpants(path)
    elif method == 'image-by-image':
        subtract_ibi.subtract3(path)
    elif method == 'iraf':
        import subtract_iraf
        subtract_iraf.subtract(path)
    else:
        print("Error: Unknown method")