#!/usr/bin/python3
from PyQt6.QtCore import (QObject, pyqtSignal, pyqtSlot, QTimer)
from image_utils import (scale_to_fit, supported_extension)
from enum import Enum
from PIL import Image
import os


class Mode(Enum):
    FILE = 1
    FOLDER = 2


class ImageProcessingWorker(QObject):
    started = pyqtSignal()
    result_image = pyqtSignal(str, float)
    finished = pyqtSignal(float)
    error = pyqtSignal(str)

    def __init__(self, input, output, mode=Mode.FILE, padding=50, tolerance=5,
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
        self.file_list = []
        self.input_folder = ""
        if self.mode == Mode.FILE:
            self.input_folder = [os.path.split(self.input)[0]]
            self.file_list = [os.path.split(self.input)[1]]
        else:
            self.input_folder = self.input
            self.file_list = [x for x in os.listdir(self.input)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)

        self._stop = False

    @pyqtSlot()
    def start(self):
        self._stop = False
        self.index = 0
        self.current_file_index = 0
        self.timer.start(500)
        print("In Start event of image processing thread")

    @pyqtSlot()
    def stop(self):
        self.timer.stop()
        self.index = 0
        self._stop = True
        self.finished.emit(100)
        print("In worker stop")

    def run(self):
        if self._stop == True:
            return

        # Check to see if we're handling single file or folder
        if os.path.exists(os.path.join(self.output, self.file_list[self.index])) and not self.force_replace:
            self.index += 1
            completion = (self.index/len(os.listdir(self.input))*100)
            self.result_image.emit(os.path.join(
                self.output, self.file_list[self.index]), completion)
            self.index += 1
            return

        completion = (self.index/len(os.listdir(self.input))*100)
        self.result_image.emit(os.path.join(
            self.output, self.file_list[self.index]), completion)
        self.index += 1

        img = Image.open(os.path.join(str(self.input_folder),
                         str(self.file_list[self.index])))

        img = scale_to_fit(img,  padding=self.padding, tolerance=self.tolerance,
                           image_size=self.image_size, mark_collisions=self.mark_collisions,
                           show_grayscale=self.show_grayscale, show_color=self.show_color,
                           write_log=self.write_log)
        img.save(os.path.join(self.output, self.file_list[self.index]))
        img.close()

        if self.index >= len(self.file_list):
            self.finished.emit(100)
