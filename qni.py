from PyQt6.QtWidgets import (QApplication, QMainWindow, QFileDialog)
from QNI_UI import Ui_MainWindowQNI
from PyQt6.QtCore import (
    QRunnable, QObject, QThreadPool, pyqtSignal, pyqtSlot)
from image_utils import (_SUPPORTED_FORMATS, scale_to_fit, supported_extension)
from enum import Enum
from PIL import Image
import sys
import os
import logging


class Mode(Enum):
    FILE = 1
    FOLDER = 2


class ImageProcessingSignals(QObject):
    def __init__(self):
        finished = pyqtSignal(int)
        result_image = pyqtSignal(QObject)
        error = pyqtSignal(QObject)


class ImageProcessingWorker(QRunnable):
    def __init__(self, input, output, mode=Mode.FILE, padding=50, tolerance=5,
                 image_size=(800, 800), force_replace=False,  mark_collisions=False,
                 show_grayscale=False, show_color=False, write_log=False):
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
        self.signals = ImageProcessingSignals()

    @pyqtSlot()
    def run(self):
        # Check to see if we're handling single file or folder
        if self.mode == Mode.FILE:
            img = Image.open(self.input)
            img = scale_to_fit(img,  padding=self.padding, tolerance=self.tolerance,
                               image_size=self.image_size, mark_collisions=self.mark_collisions,
                               show_grayscale=self.show_grayscale, show_color=self.show_color,
                               write_log=self.write_log)
            img.save(self.output if supported_extension(self.output)
                     else os.path.join(self.output, os.path.basename(self.input)))
            img.close()

        else:
            # if it's not a file, then it has to be a folder so we try to create the output location
            for index, filename in enumerate(os.listdir(self.input)):
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


class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindowQNI()
        self.ui.setupUi(self)
        self.mode = Mode.FILE

        self.ui.comboBoxExtension.addItems(_SUPPORTED_FORMATS)

        self.ui.pushButtonSelectInput.clicked.connect(self.select_input_file)
        self.ui.pushButtonSelectOutput.clicked.connect(self.select_output_file)
        self.ui.radioButtonModeFile.clicked.connect(self.select_mode)
        self.ui.radioButtonModeFolder.clicked.connect(self.select_mode)
        self.ui.spinBoxPadding.valueChanged.connect(self.change_padding)
        self.ui.pushButtonStart.clicked.connect(self.start)
        self.thread_pool = QThreadPool()

    def select_mode(self):
        if self.ui.radioButtonModeFile.isChecked():
            self.mode = Mode.FILE
            self.ui.labelInput.setText("Input File:")
            self.ui.labelOutput.setText("Output File:")
        elif self.ui.radioButtonModeFolder.isChecked():
            self.mode = Mode.FOLDER
            self.ui.labelInput.setText("Input Folder:")
            self.ui.labelOutput.setText("Output Folder:")

    def select_input_file(self):
        dlg = QFileDialog()

        if self.mode == Mode.FILE:
            self.input, _ = dlg.getOpenFileName(
                self, "Select input file.", os.getcwd())
        else:
            self.input, _ = dlg.getExistingDirectory(
                self, "Select input directory.", os.getcwd())

        self.ui.lineEditInputPath.setText(self.input)

    def select_output_file(self):
        dlg = QFileDialog()

        if self.mode == Mode.FILE:
            self.output, _ = dlg.getOpenFileName(
                self, "Select output file.", os.getcwd())
        else:
            self.output, _ = dlg.getExistingDirectory(
                self, "Select output directory.", os.getcwd())

        self.ui.lineEditOutputPath.setText(self.output)

    def change_padding(self):
        self.padding = self.ui.spinBoxPadding.value()

    def change_output_extension(self):
        self.extension = self.ui.comboBoxExtension.currentText()

    def change_force_replace(self):
        if self.ui.checkBoxReplace.isChecked():
            self.force_replace = True
        else:
            self.force_replace = False

    def change_keep_logs(self):
        if self.ui.checkBoxLogs.isChecked():
            self.force_logs = True
        else:
            self.force_logs = False

    def start(self):
        pass


logging.basicConfig(filename='journal.log',
                    encoding='utf-8', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

qni_app = QApplication(sys.argv)
qni_window = Window()
qni_window.show()
sys.exit(qni_app.exec())
