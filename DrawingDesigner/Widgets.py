from PyQt5 import QtWidgets, QtCore, QtGui


class Widgets(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(Widgets, self).__init__(*args, **kwargs)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        widget = QtWidgets.QWidget()

        self.v_layout = QtWidgets.QVBoxLayout(widget)
        self.v_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(widget)

        self.layout().addWidget(self.scroll_area)

        self.initWidgets()

    def initWidgets(self):

        label = QtWidgets.QPushButton("Label")
        button = QtWidgets.QPushButton("Button")

        self.v_layout.addWidget(label)
        self.v_layout.addWidget(button)

