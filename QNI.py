from PyQt6.QtWidgets import QAbstractItemView, QApplication, QListView, QTreeView, QWidget, QMainWindow, QFileDialog
from QNI_UI import Ui_MainWindowQNI
import sys
import os
from image_utils import _SUPPORTED_FORMATS, image_boundbox, scale_to_fit
from enum import Enum


class Mode(Enum):
    FILE = 1
    FOLDER = 2


class QNIWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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


qni_app = QApplication(sys.argv)
qni_window = QNIWindow()
qni_window.show()
sys.exit(qni_app.exec())
