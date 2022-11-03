import os
import sys
import PIL
import math
import logging
import contextlib
import getopt
from PIL import Image, ImageOps


def image_boundbox(img, bg_color=(255, 255, 255), tolerance=5):
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

    if show_grayscale_result:
        img_grayscale.show()

    img_grayscale.close()

    return (left, top, right, bottom)


def scale_to_fit(img, img_size, padding):
    width, height = img_size
    image_width, image_height = img.size

    if image_width > width or image_height > height:
        img = img.resize((width, height))

    left, top, right, bottom = image_boundbox(img)
    img_width = width - (padding*2)
    img_height = height - (padding*2)
    actual_width = abs(right - left)
    actual_height = abs(bottom - top)

    if (actual_width > actual_height):
        new_size_x = actual_width + abs(img_width - actual_width)
        increment = new_size_x - actual_width
        new_size_y = actual_height + increment
    else:
        new_size_y = actual_height + \
            abs((height - (padding*2)) - actual_height)
        increment = new_size_y - actual_height
        new_size_x = actual_width + increment

    if enable_logging:
        logging.info('Image: %s ------------------',
                     os.path.basename(filename))
        logging.info('actual_width: %d - actual_height: %d',
                     actual_width, actual_height)
        logging.info('new_size_x: %d - new_size_y: %d', new_size_x, new_size_y)
        logging.info('img_width: %d - img_height: %d', img_width, img_height)
        logging.info('left: %d - top: %d - right: %d - bottom: %d',
                     left, top, right, bottom)
        logging.info('new_size_x: %d - new_size_y: %d', new_size_x, new_size_y)
        logging.info('----------------------------\n')

    img = img.crop((left, top, right, bottom))
    img = img.resize((new_size_x, new_size_y))
    result = Image.new("RGB", (width, height), (255, 255, 255))
    paste_pos_x = math.ceil((width/2)-(new_size_x/2))
    paste_pos_y = math.ceil((height/2)-(new_size_y/2))
    result.paste(img, (paste_pos_x, paste_pos_y))
    if show_color_result:
        result.show()
    return result


def usage():
    pass


mark_collisions = False
enable_logging = False
show_grayscale_result = False
show_color_result = False
force_replace = False
save_extension = ".jpg"
image_size = (0, 0)
padding = 0
threshold = 5
input_f = os.getcwd()
output_f = os.getcwd()
directory = os.getcwd()

if __name__ == "__main__":
    print(sys.argv[1:])
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:i:o:e:t:p:lgmcr", [
                                   "help", "size=", "if=", "of=", "ext=", "threshold=", "padding="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    for o, a in opts:
        print(o, a)
        if o == "-l":
            enable_logging = True
        elif o == "-g":
            show_grayscale_result = True
        elif o == "-m":
            mark_collisions = True
        elif o == "-c":
            show_color_result = True
        elif o == "-r":
            force_replace = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif o in ("-i", "--if"):
            input_f = os.path.join(os.getcwd(), a)
        elif o in ("-o", "--of"):
            output_f = os.path.join(os.getcwd(), a)
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
        img = scale_to_fit(img, image_size, 60)
        img.save(os.path.join(os.getcwd(), output_f))
        img.close()

    elif os.path.isdir(input_f):
        # if it's not a file, then it has to be a folder so we try to create the output location
        with contextlib.suppress(Exception):
            os.mkdir(output_f)

        for index, filename in enumerate(os.listdir(input_f)):
            f = os.path.join(input_f, filename)
            if os.path.isfile(f) and f.endswith((save_extension)):
                if os.path.exists(os.path.join(output_f, filename)) and not force_replace:
                    continue

                if enable_logging:
                    print(index)
                img = Image.open(f)
                img = scale_to_fit(img, image_size, 60)
                img.save(os.path.join(os.getcwd(), output_f, filename))
                img.close()
    else:
        usage()
        sys.exit(2)

# some comment to allow commit
