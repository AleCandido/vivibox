import pathlib
import traceback

from PySide6 import QtCore, QtGui, QtWidgets

from . import extract


class FilePicker(QtWidgets.QWidget):
    def __init__(self, lab="File", default=""):
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

    def path(self):
        return pathlib.Path(self.text.text())


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Case Extract")

        self.inpicker = FilePicker("Input")
        self.outpicker = FilePicker(
            "Output", pathlib.Path.home() / "Desktop" / "extracted.xlsx"
        )

        self.layout = QtWidgets.QVBoxLayout(self)
        self.button = QtWidgets.QPushButton("Extract")

        self.layout.addWidget(self.inpicker)
        self.layout.addWidget(self.outpicker)
        self.layout.addWidget(self.button, alignment=QtCore.Qt.AlignRight)
        #  self.button.resize(1, self.button.height())

        self.button.clicked.connect(self.extract)

    def extract(self):
        try:
            extract.main(self.inpicker.path(), self.outpicker.path())
            self.success()
        except Exception as e:
            self.failure(e)

    def success(self):
        dialog = QtWidgets.QDialog(self)

        button = QtWidgets.QPushButton("Open in Files")
        out_file = QtWidgets.QLabel(f"Output: <em>{self.outpicker.path()}</em>")

        def file_browser():
            QtGui.QDesktopServices.openUrl(str(self.outpicker.path().parent))

        button.clicked.connect(file_browser)
        out_file.setTextFormat(QtCore.Qt.TextFormat.RichText)

        layout = QtWidgets.QVBoxLayout(dialog)

        out_row = QtWidgets.QHBoxLayout()
        out_row.addWidget(out_file)
        out_row.addWidget(button)

        layout.addWidget(
            QtWidgets.QLabel(
                "<strong>Extracted!</strong>", alignment=QtCore.Qt.AlignCenter
            )
        )
        layout.addLayout(out_row)

        dialog.show()

    def failure(self, exc):
        dialog = QtWidgets.QMessageBox(self)

        title = "<strong>Error..</strong>"
        subtitle = "Something has gone wrong..."
        _tb = "".join(traceback.format_tb(exc.__traceback__))
        details = f"{exc.__class__.__name__}: {exc}\n\n{_tb}"
        dialog.setText(f"{title}<br>{subtitle}")
        dialog.setDetailedText(details)
        dialog.setStyleSheet(
            """QTextEdit {
                font-family: monospace;
                min-width: 600px;
                min-height: 150px;
            }"""
        )

        dialog.resize(300, dialog.height())

        #  layout = QtWidgets.QVBoxLayout(dialog)
        #  layout.addWidget(QtWidgets.QLabel())
        #  layout.addWidget(details)

        dialog.show()
