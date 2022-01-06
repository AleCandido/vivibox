import pathlib
import traceback

from PySide6 import QtCore, QtGui, QtWidgets

from . import extract


class Extractor(QtCore.QObject):
    validated = QtCore.Signal()
    loaded = QtCore.Signal()
    finished = QtCore.Signal(str, Exception)

    def run(self, infile, outfile):
        """Long-running task."""
        try:
            extract.validate(infile, outfile)
            self.validated.emit()
            wrapdf = extract.load(infile)
            self.loaded.emit()
            extract.main(wrapdf, outfile)
            self.finished.emit("success", None)
        except Exception as e:
            self.finished.emit("failure", e)


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
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Case Extract")

        self.inpicker = FilePicker("Input")
        self.outpicker = FilePicker(
            "Output", pathlib.Path.home() / "Desktop" / "extracted.xlsx"
        )

        self.layout = QtWidgets.QVBoxLayout(self)

        self.botrow = QtWidgets.QHBoxLayout()
        self.status = QtWidgets.QLabel("")
        self.extr_button = QtWidgets.QPushButton("Extract")
        self.extr_button.clicked.connect(self.extract)
        self.botrow.addWidget(QtWidgets.QLabel())
        self.botrow.addWidget(self.status, alignment=QtCore.Qt.AlignCenter)
        self.botrow.addWidget(self.extr_button, alignment=QtCore.Qt.AlignRight)

        self.layout.addWidget(self.inpicker)
        self.layout.addWidget(self.outpicker)
        self.layout.addLayout(self.botrow)

    def extract(self):
        self.worker = Extractor()
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(
            lambda: self.worker.run(self.inpicker.path(), self.outpicker.path())
        )
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

        self.worker.validated.connect(lambda: self.status.setText("validated"))
        self.worker.loaded.connect(lambda: self.status.setText("loaded"))
        self.extr_button.setEnabled(False)
        self.thread.finished.connect(lambda: self.extr_button.setEnabled(True))
        self.thread.finished.connect(lambda: self.status.setText(""))

        def notify(res, exc):
            if res == "success":
                self.success()
            else:
                try:
                    assert res == "failure"
                except AssertionError as e:
                    exc = e
                    exc.args = (res,)
                finally:
                    self.failure(exc)

        self.worker.finished.connect(lambda r, e: notify(r, e))

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
        if isinstance(exc, FileNotFoundError):
            subtitle = f"Input file not found: '{self.inpicker.path()}'"
        elif isinstance(exc, FileExistsError):
            subtitle = f"Output file already existing: '{self.outpicker.path()}'"
        else:
            _tb = "".join(traceback.format_tb(exc.__traceback__))
            details = f"{exc.__class__.__name__}: {exc}\n\n{_tb}"
            dialog.setDetailedText(details)

        dialog.setText(f"{title}<br>{subtitle}")

        dialog.setStyleSheet(
            """QTextEdit {
                font-family: monospace;
                min-width: 600px;
                min-height: 150px;
            }"""
        )

        dialog.show()
