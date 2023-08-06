import combine_swarp
import combine_numpy

if __name__ == '__main__':
    location = input("Enter path to data directory: ")
    method = input("Choose combination method-- numpy (default), swarp, or iraf: ")
    if method == "swarp":
        combine_swarp.swarp(location)
    elif method == "numpy" or method == "":
        combine_numpy.combine_median(location)
    elif method == "iraf":
        import combine_iraf
        combine_iraf.combine(location)
    else:
        print("Error: unknown method entered")
