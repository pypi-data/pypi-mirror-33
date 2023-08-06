import align_astroalign
import align_template
from ref_image import ref_image
from initialize import loc
import subtract_hotpants
import subtract_ibi
import subtract_numpy
import combine_swarp
import combine_numpy
import sex
import check_saturation

if __name__ == '__main__':
    location = input("Enter path to data directory: ")
    sat = check_saturation.check_saturate(location)
    if sat == 0:
        ref_image(location)
        alignment = input("Enter alignment method (enter iraf or astroalign): ")
        if alignment == "iraf":
            import align_iraf
            align_iraf.align(location)
        elif alignment == "astroalign":
            align_astroalign.align2(location)
        else:
            print("Error: unknown method")
    else:
        check = input("Saturated images found, continue image alignment? (y/n): ")
        if check == 'y':
            move = input("Move saturated images to SDI archives before continuing? (y/n): ")
            if move == 'y':
                check_saturation.move_arch(sat)
                ref_image(location)
                alignment = input("Enter alignment method (enter iraf or astroalign): ")
                if alignment == "iraf":
                    import align_iraf
                    align_iraf.align(location)
                elif alignment == "astroalign":
                    align_astroalign.align2(location)
                else:
                    print("Error: unknown method")
            else:
                ref_image(location)
                alignment = input("Enter alignment method (enter iraf or astroalign): ")
                if alignment == "iraf":
                    import align_iraf
                    align_iraf.align(location)
                elif alignment == "astroalign":
                    align_astroalign.align2(location)
                else:
                    print("Error: unknown method")
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
    path = location[:-5]
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
    ask = input("Run sextractor on residual images? (y/n): ")
    if ask == 'y':
        sex.sex(path)
    elif ask != 'y' and ask != 'n':
        print("Error: unknown input")