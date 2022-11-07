# Investigate this file 2-068579.jpg
import os
import sys
import PIL
import math
import logging
import contextlib
import getopt
from PIL import Image, ImageOps

_SUPPORTED_FORMATS = [".bmp", ".dds", ".exif", ".gif", ".jpg", ".jpeg", ".jps", ".jp2",
                      ".jpx", ".pcx", ".png", ".pnm", ".ras", ".tga", ".tif", ".tiff", ".xbm", ".xpm"]


def supported_extension(input):
    for ext in _SUPPORTED_FORMATS:
        if input.endswith(ext):
            return True
    return False


def image_boundbox(img, bg_color=(255, 255, 255), tolerance=5, mark_collisions=False, show_grayscale=False):
    width = img.width
    height = img.height

    img_grayscale = ImageOps.grayscale(img)
    tolerance_range = list(range(255-tolerance+1, 256))

    # find left bound
    left = 0
    for y in range(height):
        for x in range(width):
            if img_grayscale.getpixel((x, y)) not in tolerance_range:
                if mark_collisions:
                    img_grayscale.putpixel((x, y), (0))
                if (x > left and left == 0) or (x < left and left != 0):
                    left = x
                break

    right = width
    for y in range(height):
        for x in reversed(range(width)):
            if img_grayscale.getpixel((x, y)) not in tolerance_range:
                if mark_collisions:
                    img_grayscale.putpixel((x, y), (0))
                if x < right and right == width or x > right and right != width:
                    right = x
                break

    top = 0
    for x in range(width):
        for y in range(height):
            if img_grayscale.getpixel((x, y)) not in tolerance_range:
                if mark_collisions:
                    img_grayscale.putpixel((x, y), (0))
                if y > top and top == 0 or y < top and top != 0:
                    top = y
                break

    bottom = height
    for x in range(width):
        for y in reversed(range(height)):
            if img_grayscale.getpixel((x, y)) not in tolerance_range:
                if mark_collisions:
                    img_grayscale.putpixel((x, y), (0))
                if y < bottom and bottom == height or y > bottom and bottom != height:
                    bottom = y
                break

    if show_grayscale:
        img_grayscale.show()

    img_grayscale.close()

    return (left, top, right, bottom)


def scale_to_fit(img, padding=50, tolerance=5, image_size=(800, 800), mark_collisions=False, show_grayscale=False, show_color=False, write_log=False):
    if write_log:
        logging.info('Image: %s ------------------',
                     os.path.basename(img.filename))
    # Target width/height of resulting image.
    target_width, target_height = image_size
    # Padded width/height of resulting image.
    padded_width, padded_height = (
        target_width - (2*padding), target_height - (2*padding))
    # Get rect area of object inside image.
    left, top, right, bottom = image_boundbox(
        img, tolerance=tolerance, mark_collisions=mark_collisions)
    # Crop image to contain only the object
    actual_object = img.crop((left, top, right, bottom))
    # Object width/height
    object_width, object_height = actual_object.size

    size_change_x = padded_width - object_width
    size_change_y = padded_height - object_height

    if object_width > object_height:
        new_size_x = object_width + (padded_width - object_width)
        increment = new_size_x - object_width
        new_size_y = int(object_height + (object_height *
                         (increment / object_width)))
    else:
        new_size_y = object_height + (padded_height - object_height)
        increment = new_size_y - object_height
        new_size_x = int(object_width + (object_width *
                         (increment / object_height)))

    if write_log:
        logging.info('object_width: %d - object_height: %d',
                     object_width, object_height)
        logging.info('new_size_x: %d - new_size_y: %d',
                     new_size_x, new_size_y)
        logging.info('target_width: %d - target_height: %d',
                     target_width, target_height)
        logging.info('left: %d - top: %d - right: %d - bottom: %d',
                     left, top, right, bottom)
        logging.info('new_size_x: %d - new_size_y: %d',
                     new_size_x, new_size_y)
        logging.info('----------------------------\n')

        actual_object = actual_object.resize((new_size_x, new_size_y))
        result = Image.new(
            "RGB", (target_width, target_height), (255, 255, 255))
        result.paste(actual_object, (int((target_width/2) -
                     (new_size_x / 2)), int((target_height/2) - (new_size_y/2))))
        if show_color:
            result.show()
        return result


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
            -f, --force         overwrite outputfile in case it exists. Without this this rogram does not replace
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
