# ni stands for "normalize images"

# Investigate this file 2-068579.jpg
import getopt
import sys
import os
import logging
from iu import scale_to_fit, supported_extension
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class EventHandler(FileSystemEventHandler):
    def __init__(self, output_f, padding, tolerance, image_size, mark_collisions, show_grayscale, show_color, write_log):
        self.output_f = output_f
        self.padding = padding
        self.tolerance = tolerance
        self.image_size = image_size
        self.mark_collisions = mark_collisions
        self.show_grayscale = show_grayscale
        self.show_color = show_color
        self.write_log = write_log

    def process_event(self, event):
        process_image(event.src_path, self.output_f, self.padding, self.tolerance, self.image_size,
                      self.mark_collisions, self.show_grayscale, self.show_color, self.write_log)

    def on_closed(self, event):
        self.process_event(event)

    def on_created(self, event):
        pass  # self.process_event(event)

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        pass
        # process_image(event.src_path, self.output_f, self.padding, self.tolerance, self.image_size,
        # self.mark_collisions, self.show_grayscale, self.show_color, self.write_log)

    def on_moved(self, event):
        pass
       # process_image(event.src_path, self.output_f, self.padding, self.tolerance, self.image_size,
       #               self.mark_collisions, self.show_grayscale, self.show_color, self.write_log)


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
            -w, --watch         Run script as a watcher that notices file changes in input directory and
                                outputs the result in the output directory.
    """)

    print(output_string)


def process_image(input_f, output_f, padding, tolerance, image_size, mark_collisions, show_grayscale, show_color, write_log):
    image = Image.open(input_f)
    image = scale_to_fit(image,  padding=padding, tolerance=tolerance, image_size=image_size,
                         mark_collisions=mark_collisions, show_grayscale=show_grayscale, show_color=show_color, write_log=write_log)
    image.save(output_f if supported_extension(output_f)
               else os.path.join(output_f, os.path.basename(input_f)))
    image.close()


def quit():
    usage()
    sys.exit(2)


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:i:o:e:t:p:lgmcrw", [
            "help", "size=", "if=", "of=", "ext=", "threshold=", "padding=", "watch="])
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
    watch = False

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
        elif o in ("-w", "--watch"):
            watch = True

    logging.basicConfig(filename='journal.log',
                        encoding='utf-8', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())

    if watch == True:
        if not os.path.isdir(input_f):
            quit()

        event_handler = EventHandler(
            output_f, padding, tolerance, image_size, mark_collisions, show_grayscale, show_color, write_log)
        observer = Observer()
        observer.schedule(event_handler, input_f, recursive=True)
        observer.start()

        try:
            while observer.is_alive():
                observer.join(1)
        finally:
            observer.stop()
            observer.join()

    else:
        # Check to see if we're handling single file or folder
        if os.path.isfile(input_f):
            process_image(input_f, output_f, padding, tolerance, image_size,
                          mark_collisions, show_grayscale, show_color, write_log)
        elif os.path.isdir(input_f):
            # if it's not a file, then it has to be a folder so we try to create the output location
            for index, filename in enumerate(os.listdir(input_f)):
                f = os.path.join(input_f, filename)
                if os.path.isfile(f) and supported_extension(f):
                    if os.path.exists(os.path.join(output_f, filename)) and not force_replace:
                        continue

                    if write_log:
                        print(index)
                    process_image(os.path.join(input_f, filename), output_f, padding, tolerance, image_size,
                                  mark_collisions, show_grayscale, show_color, write_log)
        else:
            quit()
