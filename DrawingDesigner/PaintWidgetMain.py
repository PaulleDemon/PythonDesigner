import sys

from PyQt5 import QtWidgets, QtGui, QtCore

from DrawingDesigner import PaintViewPort, Properties, PageTreeView
from . import Widgets
from . import Tools


class PaintWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(PaintWidget, self).__init__(*args, **kwargs)

        self.setLayout(QtWidgets.QVBoxLayout())

        tool_splitter = QtWidgets.QSplitter()
        tool_splitter.setOrientation(QtCore.Qt.Vertical)

        self.tools = Tools.Tools()

        tool_splitter.addWidget(self.tools)
        tool_splitter.addWidget(Widgets.Widgets())

        properties_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        properties_splitter.addWidget(PageTreeView.PageTreeView())
        properties_splitter.addWidget(Properties.PropertiesPanel())

        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_splitter.addWidget(tool_splitter)
        main_splitter.addWidget(PaintViewPort.ViewPort())
        main_splitter.addWidget(properties_splitter)


        self.layout().addWidget(main_splitter)



