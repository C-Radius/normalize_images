#!/usr/bin/python3
from PyQt6 import QtWidgets
from PyQt6.QtGui import QFocusEvent, QIntValidator, QValidator, QPixmap, QIcon
from PyQt6.QtWidgets import (QWidget,
                             QApplication, QMainWindow, QFileDialog, QListWidgetItem)
from QNI_UI import Ui_MainWindowQNI
from PyQt6.QtCore import QThreadPool, QThread, QSize
from iu import _SUPPORTED_FORMATS
from ipw import *
import sys
import os
import logging


class Window(QMainWindow):
    stop_thread = pyqtSignal()

    def __init__(self):
        QMainWindow.__init__(self)
        # Initialize GUI
        self.ui = Ui_MainWindowQNI()
        self.ui.setupUi(self)
        self.mode = Mode.FILE
        self.ui.comboBoxExtension.addItems(_SUPPORTED_FORMATS)

        # Default settings setup.
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
        self.output_extension = ".jpg"
        self.running = False

        # Connect signals and slots for GUI
        self.ui.pushButtonSelectInput.clicked.connect(self.select_input_file)
        self.ui.pushButtonSelectOutput.clicked.connect(self.select_output_file)
        self.ui.radioButtonModeFile.clicked.connect(self.select_mode)
        self.ui.radioButtonModeFolder.clicked.connect(self.select_mode)
        self.ui.spinBoxPadding.valueChanged.connect(self.change_padding)
        self.ui.pushButtonStart.clicked.connect(self.start)
        self.ui.pushButtonStop.clicked.connect(self.stop)
        self.ui.lineEditWidth.editingFinished.connect(self.change_output_size)
        self.ui.lineEditHeight.editingFinished.connect(self.change_output_size)
        self.ui.lineEditHeight.setValidator(QIntValidator(1, 9999999))
        self.ui.lineEditWidth.setValidator(QIntValidator(1, 9999999))

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

    def image_result(self, filename, image, completion):
        from PIL.ImageQt import ImageQt
        pixmap = QPixmap.fromImage(ImageQt(image.resize((255, 255))))
        item = QListWidgetItem()
        item.setText(os.path.split(filename)[1])
        item.setIcon(QIcon(pixmap))
        self.ui.listWidgetThumbnails.setIconSize(QSize(255, 255))
        self.ui.listWidgetThumbnails.setGridSize(QSize(4, 4))

        self.ui.listWidgetThumbnails.addItem(item)
        self.ui.statusbar.showMessage(f'Processing {filename}', 0)
        self.ui.progressBar.setValue(int(completion))

    def disable_interface(self):
        self.ui.pushButtonStop.setEnabled(True)
        self.ui.pushButtonStart.setEnabled(False)
        self.ui.checkBoxLogs.setEnabled(False)
        self.ui.checkBoxReplace.setEnabled(False)
        self.ui.pushButtonSelectInput.setEnabled(False)
        self.ui.pushButtonSelectOutput.setEnabled(False)
        self.ui.spinBoxPadding.setEnabled(False)
        self.ui.spinBoxTolerance.setEnabled(False)
        self.ui.lineEditHeight.setEnabled(False)
        self.ui.lineEditWidth.setEnabled(False)
        self.ui.lineEditInputPath.setEnabled(False)
        self.ui.lineEditOutputPath.setEnabled(False)
        self.ui.radioButtonModeFile.setEnabled(False)
        self.ui.radioButtonModeFolder.setEnabled(False)
        self.ui.comboBoxExtension.setEnabled(False)

    def enable_interface(self):
        self.ui.pushButtonStop.setEnabled(False)
        self.ui.pushButtonStart.setEnabled(True)
        self.ui.checkBoxLogs.setEnabled(True)
        self.ui.checkBoxReplace.setEnabled(True)
        self.ui.pushButtonSelectInput.setEnabled(True)
        self.ui.pushButtonSelectOutput.setEnabled(True)
        self.ui.spinBoxPadding.setEnabled(True)
        self.ui.spinBoxTolerance.setEnabled(True)
        self.ui.lineEditHeight.setEnabled(True)
        self.ui.lineEditWidth.setEnabled(True)
        self.ui.lineEditInputPath.setEnabled(True)
        self.ui.lineEditOutputPath.setEnabled(True)
        self.ui.radioButtonModeFile.setEnabled(True)
        self.ui.radioButtonModeFolder.setEnabled(True)
        self.ui.comboBoxExtension.setEnabled(True)

    def start(self):
        if self.input == "":
            return
        if self.output == "":
            return

        self.worker_thread = QThread()
        self.worker = ImageProcessingWorker(self.input, self.output, self.mode,
                                            self.padding, self.tolerance, self.image_size, self.output_extension,
                                            self.force_replace, self.mark_collisions,
                                            self.show_grayscale, self.show_color,
                                            self.write_log)

        self.worker_thread.started.connect(self.worker.start)
        self.worker.result_image.connect(self.image_result)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.stop_thread.connect(self.worker.stop)
        self.worker.moveToThread(self.worker_thread)
        self.worker.finished.connect(self.stop)

        self.worker_thread.start()
        self.disable_interface()

    def stop(self):
        self.enable_interface()
        self.stop_thread.emit()


logging.basicConfig(filename='journal.log',
                    encoding='utf-8', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

qni_app = QApplication(sys.argv)
qni_window = Window()
qni_window.show()
sys.exit(qni_app.exec())
