import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from CustomWidgets.ColorPicker import ColorCircleDialog


class Preference(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        super(Preference, self).__init__(*args, **kwargs)
        self.setModal(True)

        formLayout = QtWidgets.QFormLayout(self)

        pen_width_validator = QtGui.QRegExpValidator(QtCore.QRegExp("[1-5]\.[0-9][0-9]"))

        self.pen_width = QtWidgets.QLineEdit()
        self.pen_width.setValidator(pen_width_validator)

        self.pen_color = QtWidgets.QPushButton()
        # self.pen_color.setAutoFillBackground(True)
        # self.pen_color.setPalette(QtGui.QPalette().setColor(QtGui.QColor()))
        self.pen_color.clicked.connect(self.colorDialog)

        self.grid_background_color = QtWidgets.QPushButton()
        self.grid_background_color.setAutoFillBackground(True)
        self.grid_background_color.clicked.connect(self.colorDialog)

        self.defalut_path = QtWidgets.QComboBox()
        self.defalut_path.addItems(["Direct", "Bezier", "Square"])

        self.path_color = QtWidgets.QPushButton(clicked=self.colorDialog)
        self.node_header_fg_color = QtWidgets.QPushButton(clicked=self.colorDialog)
        self.node_header_color = QtWidgets.QPushButton(clicked=self.colorDialog)
        self.node_body_fg_color = QtWidgets.QPushButton(clicked=self.colorDialog)
        self.node_body_color = QtWidgets.QPushButton(clicked=self.colorDialog)

        formLayout.addRow(QtWidgets.QLabel("Grid: "))
        formLayout.addRow(QtWidgets.QLabel("Pen width: "), self.pen_width)
        formLayout.addRow(QtWidgets.QLabel("Grid line color: "), self.pen_color)
        formLayout.addRow(QtWidgets.QLabel("Grid background: "), self.grid_background_color)

        formLayout.addRow(QtWidgets.QLabel("Path: "))
        formLayout.addRow(QtWidgets.QLabel("Default Path: "), self.defalut_path)
        formLayout.addRow(QtWidgets.QLabel("Path color: "), self.path_color)

        formLayout.addRow(QtWidgets.QLabel("Node: "))
        formLayout.addRow(QtWidgets.QLabel("Node header foreground: "), self.node_header_fg_color)
        formLayout.addRow(QtWidgets.QLabel("Node header background: "), self.node_header_color)
        formLayout.addRow(QtWidgets.QLabel("Node body foreground: "), self.node_body_fg_color)
        formLayout.addRow(QtWidgets.QLabel("Node body background: "), self.node_body_color)


    def colorDialog(self):
        widget = self.sender()
        self.win = ColorCircleDialog(self)
        self.win.currentColorChanged.connect(lambda color: self.changeBtnColor(color, widget))

        pos = self.mapToGlobal(QtCore.QPoint(widget.geometry().center().x(), widget.geometry().bottom()))

        self.win.move(pos)
        self.win.show()
        # self.win.exec()

    def changeBtnColor(self, color, widget):
        widget.setStyleSheet(f"background-color: {color.name()}; "
                             f"border-radius: 2px; min-height: 25px; border: 2px solid #ffffff")
        # palette = widget.palette()
        # palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(color))
        # widget.setPalette(palette)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    win = Preference()
    win.show()

    sys.exit(app.exec())
