import math

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtProperty


# EDGE_CP_ROUNDNESS = 100     #: Bezier control point distance on the line
EDGE_CP_ROUNDNESS = 200     #: Bezier control point distance on the line
# WEIGHT_SOURCE = 0.2         #: factor for square edge to change the midpoint between start and end socket
WEIGHT_SOURCE = 0.2         #: factor for square edge to change the midpoint between start and end socket


DIRECT_PATH = 0
BEZIER_PATH = 1
SQUARE_PATH = 2


class Path(QtWidgets.QGraphicsPathItem):

    pathChanged = QtCore.pyqtSignal()

    def __init__(self, source: QtCore.QPointF = None, destination: QtCore.QPointF = None, path_type = BEZIER_PATH,
                *args, **kwargs):

        super(Path, self).__init__(*args, **kwargs)

        self._source = source
        self._destination = destination

        self._path_color = QtGui.QColor("#000000")
        self._selection_color = QtGui.QColor("#03a81c")
        self._hover_Color = QtGui.QColor("#03a81c")

        self._pen_width = 2.4
        self._path_type = path_type

        self._handle_weight = 0.5

        self._hovered = False

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable)

        self.setAcceptHoverEvents(True)

        self._arrow_height = 5
        self._arrow_width = 4

    def pathColor(self):
        return self._path_color

    def setPathColor(self, color: QtGui.QColor):
        self._path_color = color

    def penWidth(self):
        return self._pen_width

    def hoverColor(self):
        return self._hover_Color

    def setHoverColor(self, color: QtGui.QColor):
        self._hover_Color = color

    def selectionColor(self):
        return self._selection_color

    def setSelectionColor(self, color: QtGui.QColor):
        self._selection_color = color

    def setPenWidth(self, width: float):
        self._pen_width = width

    PathColor = pyqtProperty(QtGui.QColor, pathColor, setPathColor)
    PathHoverColor = pyqtProperty(QtGui.QColor, hoverColor, setHoverColor)
    SelectionColor = pyqtProperty(QtGui.QColor, selectionColor, setSelectionColor)

    PathWidth = pyqtProperty(float, penWidth, setPenWidth)

    def getSourcePoints(self):
        return self._source

    def setSourcePoints(self, source: QtCore.QPointF):
        self._source = source

    def getDestinationPoints(self):
        return self._destination

    def setDestinationPoints(self, destination: QtCore.QPointF):
        self._destination = destination

    def setPathType(self, type=DIRECT_PATH):

        if type not in [DIRECT_PATH, BEZIER_PATH, SQUARE_PATH]:
            raise Exception(f"Invalid Path Type: {type}")
            return

        self._path_type = type
        self.update(self.sceneBoundingRect())
        # self.pathChanged.emit()

    def setSquarePathHandleWeight(self, weight: float):
        self._handle_weight = weight

    def getArrowProperties(self):
        return self._arrow_height, self._arrow_width

    def setArrowProperties(self, height, width):
        self._arrow_height, self._arrow_width = height, width

    def hoverEnterEvent(self, event) -> None:
        self._hovered = True
        self.update(self.sceneBoundingRect())
        super(Path, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        self._hovered = False
        self.update(self.sceneBoundingRect())
        super(Path, self).hoverLeaveEvent(event)

    def contextMenuEvent(self, event) -> None:
        menu = QtWidgets.QMenu()

        direct_path = QtWidgets.QAction("Direct Path")
        direct_path.triggered.connect(lambda: self.setPathType(DIRECT_PATH))

        bezier_path = QtWidgets.QAction("Bezier Path")
        bezier_path.triggered.connect(lambda: self.setPathType(BEZIER_PATH))

        square_path = QtWidgets.QAction("Square Path")
        square_path.triggered.connect(lambda: self.setPathType(SQUARE_PATH))

        menu.addActions([direct_path, bezier_path, square_path])

        menu.exec(event.screenPos())

    def arrowCalc(self, start_point=None, end_point=None, drawAT=1):
        # if draw at is 1 then the arrow will be drawn at the end


        try:
            startPoint, endPoint = start_point, end_point

            if start_point is None:
                startPoint = self.getSourcePoints()

            if endPoint is None:
                endPoint = self.getDestinationPoints()

            dx, dy = startPoint.x()-endPoint.x(), startPoint.y()-endPoint.y()

            leng = math.sqrt(dx**2 + dy**2)
            print("Leng: ", leng)
            normX, normY = dx/leng, dy/leng  # normalize

            # perpendicular vector
            perpX = -normY
            perpY = normX

            end = startPoint if drawAT == 0 else endPoint

            leftX = end.x() + self._arrow_height * normX + self._arrow_width * perpX
            leftY = end.y() + self._arrow_height * normY + self._arrow_width * perpY

            rightX = end.x() + self._arrow_height * normX - self._arrow_height * perpX
            rightY = end.y() + self._arrow_height * normY - self._arrow_width * perpY

            point2 = QtCore.QPointF(leftX, leftY)
            point3 = QtCore.QPointF(rightX, rightY)

            return QtGui.QPolygonF([point2,  end, point3])

        except ZeroDivisionError:
            return None

    def squarePath(self):
        s = self.getSourcePoints()
        d = self.getDestinationPoints()

        mid_x = s.x() + ((d.x() - s.x()) * self._handle_weight)

        path = QtGui.QPainterPath(QtCore.QPointF(s.x(), s.y()))
        path.lineTo(mid_x, s.y())
        path.lineTo(mid_x, d.y())
        path.lineTo(d.x(), d.y())

        return path

    def directPath(self):
        start_point = self.getSourcePoints()
        end_point = self.getDestinationPoints()
        path = QtGui.QPainterPath(start_point)
        path.lineTo(end_point)

        return path

    def bezierPath(self):
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
        # path.cubicTo(source_x + cpx_s, source_y + cpy_s, destination_x + cpx_d, destination_y + cpy_d,
        #              destination_x, destination_y)

        path.cubicTo(destination_x + cpx_d, destination_y + cpy_d, source_x + cpx_s, source_y + cpy_s,
                     destination_x, destination_y)

        # arrowHead = self.arrowCalc(path.pointAtPercent(0.9), QtCore.QPointF(destination_x, destination_y))

        print("Point At: ", path.pointAtPercent(0.9), destination_y, destination_x)

        return path

    def calcPath(self):

        if self._path_type == DIRECT_PATH:
            return self.directPath()

        elif self._path_type == BEZIER_PATH:
            return self.bezierPath()

        else:
            return self.squarePath()

    def paint(self, painter: QtGui.QPainter, option, widget=None) -> None:

        pen = QtGui.QPen(QtGui.QPen(self._path_color, self._pen_width))

        painter.setRenderHint(painter.Antialiasing)

        if self.isSelected():
            pen.setColor(QtGui.QColor(self._selection_color))

        if self._hovered:
            pen.setColor(QtGui.QColor(self._hover_Color))

        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)

        path = self.calcPath()
        painter.drawPath(path)
        self.setPath(path)

        triangle = self.arrowCalc(path.pointAtPercent(0.9), self.getDestinationPoints())
        # painter.drawPolygon(triangle)
        if triangle is not  None:
            painter.drawPolyline(triangle)
