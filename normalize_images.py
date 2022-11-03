import os
import PIL
import math
import logging
import contextlib
from PIL import Image, ImageOps

SHOW_GRAYSCALE_RESULT = False
MARK_COLLISIONS = False
ENABLE_LOGGING = True

directory = os.path.join(os.getcwd(), "source")


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
                if MARK_COLLISIONS:
                    img_grayscale.putpixel((x, y), (0))
                if (x > left and left == 0) or (x < left and left != 0):
                    left = x
                break

    right = width
    for y in range(height):
        for x in reversed(range(width)):
            if img_grayscale.getpixel((x, y)) not in tolerance_range:
                if MARK_COLLISIONS:
                    img_grayscale.putpixel((x, y), (0))
                if x < right and right == width or x > right and right != width:
                    right = x
                break

    top = 0
    for x in range(width):
        for y in range(height):
            if img_grayscale.getpixel((x, y)) not in tolerance_range:
                if MARK_COLLISIONS:
                    img_grayscale.putpixel((x, y), (0))
                if y > top and top == 0 or y < top and top != 0:
                    top = y
                break

    bottom = height
    for x in range(width):
        for y in reversed(range(height)):
            if img_grayscale.getpixel((x, y)) not in tolerance_range:
                if MARK_COLLISIONS:
                    img_grayscale.putpixel((x, y), (0))
                if y < bottom and bottom == height or y > bottom and bottom != height:
                    bottom = y
                break

    if SHOW_GRAYSCALE_RESULT:
        img_grayscale.show()

    img_grayscale.close()

    return (left, top, right, bottom)


def scale_to_fit(filename, width, height, padding):
    img = Image.open(filename)
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

    if ENABLE_LOGGING:
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
    result.save(os.path.join("output", os.path.basename(f)), "JPEG")
    result.close()


if __name__ == "__main__":
    logging.basicConfig(filename='journal.log',
                        encoding='utf-8', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())

    with contextlib.suppress(Exception):
        os.mkdir("output")

    for index, filename in enumerate(os.listdir(directory)):
        if ENABLE_LOGGING:
            print(index)

        f = os.path.join(directory, filename)
        if os.path.isfile(f) and f.endswith((".jpg")) and not os.path.exists(os.path.join(os.getcwd(), "output", filename)):
            scale_to_fit(os.path.join(
                os.getcwd(), "source", filename), 800, 800, 60)

#some comment to allow commit
