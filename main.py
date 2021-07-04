import sys
from PyQt5 import QtWidgets
from Windows.MainWindow import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    wind = MainWindow()
    wind.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
