#!/usr/bin/python3
from PyQt6.QtCore import (QObject, pyqtSignal, pyqtSlot, QTimer)
from image_utils import (scale_to_fit, supported_extension)
from enum import Enum
from PIL import Image
import os


class Mode(Enum):
    FILE = 1
    FOLDER = 2


class ImageProcessingSignals(QObject):
    started = pyqtSignal(int)
    finished = pyqtSignal(int)
    result_image = pyqtSignal(str, float)
    error = pyqtSignal(str)

    def __init__(self, running_event, input, output, mode=Mode.FILE, padding=50, tolerance=5,
                 image_size=(800, 800), force_replace=False,  mark_collisions=False,
                 show_grayscale=False, show_color=False, write_log=False):
        super().__init__()
        self.input = input
        self.output = output
        self.mode = mode
        self.padding = padding
        self.tolerance = tolerance
        self.image_size = image_size
        self.force_replace = force_replace
        self.mark_collisions = mark_collisions
        self.show_grayscale = show_grayscale
        self.show_color = show_color
        self.write_log = write_log

    @pyqtSlot()
    def start(self):
        self.file_list = os.listdir(self.input)
        self.current_file_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.run)
        self.timer.start(100)

    @pyqtSlot()
    def stop(self):
        self.timer.stop()

    @pyqtSlot()
    def run(self):
        # Check to see if we're handling single file or folder
        self.started.emit(True)

        if self.mode == Mode.FILE:
            img = Image.open(self.input)
            img = scale_to_fit(img,  padding=self.padding, tolerance=self.tolerance,
                               image_size=self.image_size, mark_collisions=self.mark_collisions,
                               show_grayscale=self.show_grayscale, show_color=self.show_color,
                               write_log=self.write_log)
            img.save(self.output if supported_extension(self.output)
                     else os.path.join(self.output, os.path.basename(self.input)))
            img.close()

            self.result_image.emit(self.input, 100.0)

        else:
            # if it's not a file, then it has to be a folder so we try to create the output location
            for index, filename in enumerate(os.listdir(self.input)):
                if self.running_event.
                f = os.path.join(self.input, filename)
                if os.path.isfile(f) and supported_extension(f):
                    if os.path.exists(os.path.join(self.output, filename)) and not self.force_replace:
                        continue

                    if self.write_log:
                        print(index)
                    img = Image.open(f)
                    img = scale_to_fit(img, padding=self.padding, tolerance=self.tolerance,
                                       image_size=self.image_size, mark_collisions=self.mark_collisions,
                                       show_grayscale=self.show_grayscale, show_color=self.show_color,
                                       write_log=self.write_log)
                    img.save(os.path.join(os.getcwd(), self.output, filename))
                    img.close()
                    completion = (index/len(os.listdir(self.input))*100)
                    self.result_image.emit(
                        filename, completion)
                    print(f'Completion {completion}')

        self.finished.emit(True)
