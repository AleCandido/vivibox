import sys

from PySide6 import QtWidgets
from case_log_extract import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MainWindow()
    widget.resize(600, 0)
    widget.show()

    sys.exit(app.exec())
