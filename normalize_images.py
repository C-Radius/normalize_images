# Investigate this file 2-068579.jpg
import getopt
import sys
import os
import logging
from image_utils import scale_to_fit, supported_extension
from PIL import Image


def usage():
    import inspect
    output_string = inspect.cleandoc("""
        Utility to normalize images in a set image size
        options:
            -s, --size          used to set the target image size. Must be passed as a string with two values
                                Eg: -s "800 800"
            -i, --input         Input file location. If file location is file it will use single image mode.
                                If input file location is a folder, all files in the folder will be processed.
            -o, --output        Can be directory where the image will be stored with the same name.
                                Or it can be a folder where all images will be store at.
            -t, --tolerance     Used to control how much tolerance in color values the algorithm will have.
                                The bigger the tolerance the less pixels will pass the algorithm's test.
            -p, --padding       How much wite space witll the result image have around the object.
            -l, --logging       Enable's logging of information about the image. In terminal and in output
                                file.
            -f, --force         overwrite outputfile in case it exists. Without this program does not replace
                                images.
            -c                  Show output image. Usually for fast check of the result.
            -g                  Show grayscale image.
            -m                  Keep track of collisions and show them in grayscale result.
            -h, --help          Shows this manual. 
    """)

    print(output_string)


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:i:o:e:t:p:lgmcr", [
            "help", "size=", "if=", "of=", "ext=", "threshold=", "padding="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    write_log = False
    show_grayscale = False
    mark_collisions = False
    show_color = False
    force_replace = False
    input_f = os.getcwd()
    output_f = os.getcwd()
    padding = 50
    image_size = (800, 800)
    tolerance = 5

    for o, a in opts:
        if o == "-l":
            write_log = True
        elif o == "-g":
            show_grayscale = True
        elif o == "-m":
            mark_collisions = True
        elif o == "-c":
            show_color = True
        elif o == "-r":
            force_replace = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif o in ("-i", "--if"):
            input_f = a
        elif o in ("-o", "--of"):
            output_f = a
        elif o in ("-e", "--ext"):
            save_extension = a
        elif o in ("-t", "--threshold"):
            threshold = int(a)
        elif o in ("-p", "--padding"):
            padding = int(a)
        elif o in ("-s", "--size"):
            image_size = tuple(int(x) for x in a.split(" "))

    logging.basicConfig(filename='journal.log',
                        encoding='utf-8', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())

    # Check to see if we're handling single file or folder
    if os.path.isfile(input_f):
        img = Image.open(input_f)
        img = scale_to_fit(img,  padding=padding, tolerance=tolerance, image_size=image_size,
                           mark_collisions=mark_collisions, show_grayscale=show_grayscale, show_color=show_color, write_log=write_log)
        img.save(output_f if supported_extension(output_f)
                 else os.path.join(output_f, os.path.basename(input_f)))
        img.close()

    elif os.path.isdir(input_f):
        # if it's not a file, then it has to be a folder so we try to create the output location
        for index, filename in enumerate(os.listdir(input_f)):
            f = os.path.join(input_f, filename)
            if os.path.isfile(f) and supported_extension(f):
                if os.path.exists(os.path.join(output_f, filename)) and not force_replace:
                    continue

                if write_log:
                    print(index)
                img = Image.open(f)
                img = scale_to_fit(img,  padding=padding, tolerance=tolerance, image_size=image_size,
                                   mark_collisions=mark_collisions, show_grayscale=show_grayscale, show_color=show_color, write_log=write_log)
                img.save(os.path.join(os.getcwd(), output_f, filename))
                img.close()
    else:
        usage()
        sys.exit(2)
