#!/usr/bin/python3
from PyQt6.QtGui import QFocusEvent, QIntValidator, QValidator
from PyQt6.QtWidgets import (QApplication, QMainWindow, QFileDialog)
from QNI_UI import Ui_MainWindowQNI
from PyQt6.QtCore import QThreadPool
from image_utils import _SUPPORTED_FORMATS
from image_processing_worker import *
import sys
import os
import logging


class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.ui = Ui_MainWindowQNI()
        self.ui.setupUi(self)
        self.mode = Mode.FILE

        self.ui.comboBoxExtension.addItems(_SUPPORTED_FORMATS)

        self.input = ""
        self.output = ""
        self.mode = Mode.FILE
        self.padding = 50
        self.tolerance = 10
        self.image_size = (800, 800)
        self.force_replace = False
        self.mark_collisions = True
        self.show_grayscale = False
        self.show_color = False
        self.write_log = False

        self.ui.pushButtonSelectInput.clicked.connect(self.select_input_file)
        self.ui.pushButtonSelectOutput.clicked.connect(self.select_output_file)
        self.ui.radioButtonModeFile.clicked.connect(self.select_mode)
        self.ui.radioButtonModeFolder.clicked.connect(self.select_mode)
        self.ui.spinBoxPadding.valueChanged.connect(self.change_padding)
        self.ui.pushButtonStart.clicked.connect(self.start)
        self.ui.lineEditWidth.editingFinished.connect(self.change_output_size)
        self.ui.lineEditHeight.editingFinished.connect(self.change_output_size)

        self.ui.lineEditHeight.setValidator(QIntValidator(1, 9999999))
        self.ui.lineEditWidth.setValidator(QIntValidator(1, 9999999))

        self.thread_pool = QThreadPool(self)

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
            self.input = dlg.getExistingDirectory(
                self, "Select input directory.", os.getcwd())

        self.ui.lineEditInputPath.setText(self.input)

    def select_output_file(self):
        dlg = QFileDialog()

        self.output = dlg.getExistingDirectory(
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

    def change_output_size(self):
        width = self.ui.lineEditWidth.text()
        height = self.ui.lineEditHeight.text()

        if width == "":
            width = 800

        if height == "":
            height = 800

        width = int(width)
        height = int(height)

        if width > 0:
            self.image_size = (width, self.image_size[1])
        else:
            self.image_Size = (800, self.image_size[1])

        if height > 0:
            self.image_size = (self.image_size[0], height)
        else:
            self.image_Size = (self.image_size[0], 800)

        if width == None:
            width = 800
        if height == None:
            height = 800

        self.ui.lineEditWidth.setText(str(self.image_size[0]))
        self.ui.lineEditHeight.setText(str(self.image_size[1]))
        print(self.image_size)

    def started(self, data):
        pass

    def finished(self, data):
        pass

    def image_result(self, filename, completion):
        self.ui.statusbar.showMessage(f'Processing {filename}', 0)
        self.ui.progressBar.setValue(int(completion))

    def start(self):
        if self.input == "":
            return
        if self.output == "":
            return

        self.ui.pushButtonStart.setText("Stop")
        self.ui.pushButtonStart.setStyleSheet(
            "background-color: rgb(200, 50, 50)")
        worker = ImageProcessingWorker(self.input, self.output, self.mode, self.padding,
                                       10, (800, 800), self.force_replace, False, False, False, True)
        worker.signals.started.connect(self.started)
        worker.signals.finished.connect(self.finished)
        worker.signals.result_image.connect(self.image_result)
        self.thread_pool.start(worker)


logging.basicConfig(filename='journal.log',
                    encoding='utf-8', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

qni_app = QApplication(sys.argv)
qni_window = Window()
qni_window.show()
sys.exit(qni_app.exec())
