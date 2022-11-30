# iu stands for "image utils"
import logging
import os
from PIL import ImageOps, Image


_SUPPORTED_FORMATS = [".jpg", ".jpeg", ".bmp", ".dds", ".exif", ".gif",  ".jps", ".jp2",
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
        for x in reversed(range(left, width)):
            if img_grayscale.getpixel((x, y)) not in tolerance_range:
                if mark_collisions:
                    img_grayscale.putpixel((x, y), (0))
                if x < right and right == width or x > right and right != width:
                    right = x
                break

    top = 0
    for x in range(left, right):
        for y in range(height):
            if img_grayscale.getpixel((x, y)) not in tolerance_range:
                if mark_collisions:
                    img_grayscale.putpixel((x, y), (0))
                if y > top and top == 0 or y < top and top != 0:
                    top = y
                break

    bottom = height
    for x in range(left, right):
        for y in reversed(range(top, height)):
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
        img, tolerance=tolerance, mark_collisions=mark_collisions, show_grayscale=show_grayscale)
    # Crop image to contain only the object
    actual_object = img.crop((left, top, right, bottom))
    # Object width/height
    object_width, object_height = actual_object.size

    size_change_x = padded_width - object_width
    size_change_y = padded_height - object_height

    if object_width > object_height:
        new_size_x = object_width + size_change_x
        increment = new_size_x - object_width
        new_size_y = int(object_height + (object_height *
                         (increment / object_width)))
    else:
        new_size_y = object_height + size_change_y
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
