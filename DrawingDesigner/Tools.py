import sys

from PyQt5 import QtWidgets, QtCore
from CustomWidgets import ButtonGroup

COLUMNS = 4


class Tools(QtWidgets.QWidget):

    toolChanged = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Tools, self).__init__(*args, **kwargs)

        widget = QtWidgets.QWidget()

        # self.grid_layout = QtWidgets.QGridLayout(widget)
        self._vlayout = QtWidgets.QVBoxLayout(widget)
        self._vlayout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(widget)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.scroll_area)

        self.initTools()

    # def addTool(self, tool: QtWidgets.QPushButton):
    #     self.grid_layout.addWidget(tool, (self.grid_layout.columnCount()-1)//COLUMNS, self.grid_layout.columnCount())

    def initTools(self):
        btn_grp = ButtonGroup.ButtonGroup(ButtonGroup.GRID_LAYOUT)
        btn_grp.setFixedBtnSize(QtCore.QSize(50, 50))

        tool_list = []

        line = QtWidgets.QPushButton("Line")
        rectangle = QtWidgets.QPushButton("Rect")
        circle = QtWidgets.QPushButton("Circle")
        rounded_rect = QtWidgets.QPushButton("Rounded Square")
        bucket_fill = QtWidgets.QPushButton("Bucket Fill")
        gradient = QtWidgets.QPushButton("Gradient")
        text = QtWidgets.QPushButton("Text")
        paintBrush = QtWidgets.QPushButton("Brush")
        eraser = QtWidgets.QPushButton("Eraser")

        tool_list.extend([line, rectangle, circle, rounded_rect, bucket_fill, gradient, text, paintBrush, eraser])

        for index, tool in enumerate(tool_list):
            # btn_grp.addToGroup(tool, row=btn_grp.gridCount()[1]//COLUMNS, column=(btn_grp.gridCount()[1]-1)%COLUMNS)
            btn_grp.addToGroup(tool, row=index//COLUMNS, column=index%COLUMNS)

        # btn_grp.addToGroup(line, row=0, column=0)
        self._vlayout.addWidget(btn_grp)
        print("YES")


