import align_astroalign
import align_template
from ref_image import ref_image
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