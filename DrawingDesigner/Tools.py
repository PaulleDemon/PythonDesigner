import sys

from PyQt5 import QtWidgets, QtCore, QtGui

from Resources import ResourcePaths
from CustomWidgets import ButtonGroup

COLUMNS = 4

SELECT_TOOL = 0
LINE_TOOL = 1
RECTANGLE_TOOL = 2
ELLIPSE_TOOL = 3
BUCKET_TOOL = 4
GRADIENT_TOOL = 5
TEXT = 6
PAINT_BRUSH = 7
ERASER = 8


class Tools(QtWidgets.QWidget):

    toolChanged = QtCore.pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(Tools, self).__init__(*args, **kwargs)

        widget = QtWidgets.QWidget()

        self.tools_dict = {}

        # self.grid_layout = QtWidgets.QGridLayout(widget)
        self._vlayout = QtWidgets.QVBoxLayout(widget)
        self._vlayout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(widget)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.scroll_area)

        self.current_tool = 0

        self.initTools()

    # def addTool(self, tool: QtWidgets.QPushButton):
    #     self.grid_layout.addWidget(tool, (self.grid_layout.columnCount()-1)//COLUMNS, self.grid_layout.columnCount())

    def initTools(self):
        btn_grp = ButtonGroup.ButtonGroup(layout=ButtonGroup.GRID_LAYOUT)
        btn_grp.setFixedBtnSize(QtCore.QSize(75, 75))

        tool_list = []
        tooltips = []

        line = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.LINE_TOOL))
        rectangle = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.RECTANGLE_TOOL))
        ellipse = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.ELLIPSE_TOOL))
        rounded_rect = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.ROUNDED_RECTANGLE))
        bucket_fill = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.PAINT_BUCKET_TOOL))
        gradient = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.GRADIENT_TOOL))
        text = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.TEXT))
        paintBrush = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.PAINT_BRUSH_TOOL))
        eraser = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.ERASER_TOOL))

        bucket_fill.toggled.connect(lambda: print("YAAAA"))

        tool_list.extend([line, rectangle, ellipse, rounded_rect, bucket_fill, gradient, text, paintBrush, eraser])

        tooltips.extend(["Line", "Rectangle", "Ellipse", "Rounded rectangle", "Bucket fill",
                         "Gradient", "Text", "Paint Brush", "Eraser"])

        for index, (tool, infotip) in enumerate(zip(tool_list, tooltips)):
            btn_grp.addToGroup(tool, toolTip=infotip, row=index//COLUMNS, column=index%COLUMNS)
            # tool.toggled.connect(lambda state, i=index: self.changeTool(i))

            self.tools_dict[index] = index

        # btn_grp.setDefaultButton(line)
        self._vlayout.addWidget(btn_grp)

    def changeTool(self, index):
        self.current_tool = index
        self.toolChanged.emit(index)
        print("Index", index)

    def getCurrentTool(self):
        return self.current_tool
