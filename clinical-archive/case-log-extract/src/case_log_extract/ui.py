import pathlib

from PySide6 import QtCore, QtGui, QtWidgets


class FilePicker(QtWidgets.QWidget):
    def __init__(self, text, lab="File", default=""):
        super().__init__()

        self.layout = QtWidgets.QHBoxLayout(self)

        self.label = QtWidgets.QLabel(lab + ": ")
        self.button = QtWidgets.QPushButton("Select")
        self.text = QtWidgets.QLineEdit(str(default))

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.select)

    @QtCore.Slot()
    def select(self):
        chosen, kind = QtWidgets.QFileDialog.getOpenFileName(self)
        self.text.setText(chosen)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Case Extract")

        self.input_file = ""
        self.output_file = pathlib.Path.home() / "Desktop" / "extracted.xlsx"

        self.layout = QtWidgets.QVBoxLayout(self)
        self.button = QtWidgets.QPushButton("Extract")

        self.layout.addWidget(FilePicker(self.input_file, "Input"))
        self.layout.addWidget(
            FilePicker(self.output_file, "Output", default=self.output_file)
        )
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.extract)

    @QtCore.Slot()
    def extract(self):
        dialog = QtWidgets.QDialog(self)

        button = QtWidgets.QPushButton("Open in Files")

        def file_browser():
            QtGui.QDesktopServices.openUrl(str(self.output_file.parent))

        button.clicked.connect(file_browser)

        layout = QtWidgets.QVBoxLayout(dialog, alignment=QtCore.Qt.AlignCenter)

        out_row = QtWidgets.QHBoxLayout()
        out_row.addWidget(QtWidgets.QLabel(f"Output: {self.output_file}"))
        out_row.addWidget(button)

        layout.addWidget(QtWidgets.QLabel("Extracted!"))
        layout.addLayout(out_row)

        dialog.show()
