from PySide6.QtWidgets import QApplication
from attendance_program import MainWindow

if __name__ == "__main__":
    """ Run the application. """
    import sys

    app = QApplication(sys.argv)
    app.setStyle("Material")
    mw = MainWindow()
    mw.show()

    with open("./style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    sys.exit(app.exec())
