import math

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtProperty


EDGE_CP_ROUNDNESS = 100     #: Bezier control point distance on the line
WEIGHT_SOURCE = 0.2         #: factor for square edge to change the midpoint between start and end socket


class Path(QtWidgets.QGraphicsPathItem):
    
    def __init__(self, source: QtCore.QPointF = None, destination: QtCore.QPointF = None, *args, **kwargs):
        super(Path, self).__init__(*args, **kwargs)

        self._source = source
        self._destination = destination

        self._path_color = QtGui.QColor("#000000")
        self._selection_color = QtGui.QColor("red")
        self._pen_width = 2

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)

    def pathColor(self):
        return self._path_color

    def setPathColor(self, color: QtGui.QColor):
        self._path_color = color

    def penWidth(self):
        return self._pen_width

    def setPenWidth(self, width: float):
        self._pen_width = width

    PathColor = pyqtProperty(QtGui.QColor, pathColor, setPathColor)
    PathWidth = pyqtProperty(float, penWidth, setPenWidth)

    def getSourcePoints(self):
        return self._source

    def setSourcePoints(self, source: QtCore.QPointF):
        self._source = source

    def getDestinationPoints(self):
        return self._destination

    def setDestinationPoints(self, destination: QtCore.QPointF):
        self._destination = destination

    def calcPath(self):
        raise NotImplementedError("This method has to be implemented in the child class")

    def paint(self, painter: QtGui.QPainter, option, widget=None) -> None:

        pen = QtGui.QPen(QtGui.QPen(self._path_color, self._pen_width))

        if self.isSelected():
            pen.setColor(QtGui.QColor(self._selection_color))

        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)

        path = self.calcPath()

        painter.drawPath(path)
        self.setPath(path)


class DirectPath(Path):

    def calcPath(self):

        start_point = self.getSourcePoints()
        end_point = self.getDestinationPoints()
        path = QtGui.QPainterPath(start_point)
        path.lineTo(end_point)

        return path


class BezierPath(Path):

    def calcPath(self):

        s = self.getSourcePoints()
        d = self.getDestinationPoints()

        source_x, source_y = s.x(), s.y()
        destination_x, destination_y = d.x(), d.y()

        dist = (d.x() - s.x()) * 0.5

        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if (s.x() > d.x()) or (s.x() < d.x()):
            cpx_d *= -1
            cpx_s *= -1

            cpy_d = (
                        (s.y() - d.y()) / math.fabs(
                        (s.y() - d.y()) if (s.y() - d.y()) != 0 else 0.00001
                    )
                    ) * EDGE_CP_ROUNDNESS

            cpy_s = (
                         (d.y() - s.y()) / math.fabs(
                        (d.y() - s.y()) if (d.y() - s.y()) != 0 else 0.00001
                    )
                    ) * EDGE_CP_ROUNDNESS

        path = QtGui.QPainterPath(self.getSourcePoints())
        path.cubicTo(source_x + cpx_s, source_y + cpy_s, destination_x + cpx_d, destination_y + cpy_d,
                     destination_x, destination_y)

        return path


class SquarePath(Path):

    # def __init__(self, handle_weight = 0.5, *args, **kwargs):
    #     super(SquarePath, self).__init__(*args, *kwargs)
    #
    #     self.handle_weight = handle_weight

    def calcPath(self):
        s = self.getSourcePoints()
        d = self.getDestinationPoints()

        print("SOurce: ", s, d)

        # mid_x = s.x() + ((d.x() - s.x()) * self.handle_weight)
        mid_x = s.x() + ((d.x() - s.x()) * 0.5)

        path = QtGui.QPainterPath(QtCore.QPointF(s.x(), s.y()))
        path.lineTo(mid_x, s.y())
        path.lineTo(mid_x, d.y())
        path.lineTo(d.x(), d.y())

        return path


