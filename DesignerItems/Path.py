import math
from collections import OrderedDict

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtProperty

EDGE_ROUNDNESS = 150  #: Bezier control point distance on the line
WEIGHT_SOURCE = 0.2  #: factor for square edge to change the midpoint between start and end socket

DIRECT_PATH = 0
BEZIER_PATH = 1
SQUARE_PATH = 2

SOURCE_HEADED = 0  # arrow type single headed means single arrow at the source
DESTINATION_HEADED = 1  # arrow type single headed means single arrow at the destination
DOUBLE_HEADED = 2  # double headed arrow type

zValue = 0


class Path(QtWidgets.QGraphicsPathItem):
    pathChanged = QtCore.pyqtSignal()

    def __init__(self, source: QtCore.QPointF = None, destination: QtCore.QPointF = None, path_type=BEZIER_PATH,
                 *args, **kwargs):

        super(Path, self).__init__(*args, **kwargs)

        self._sourcePoint = source
        self._destinationPoint = destination
        self._arrow_type = DESTINATION_HEADED

        self._path_color = QtGui.QColor("#000000")
        self._selection_color = QtGui.QColor("#03a81c")
        self._hover_Color = QtGui.QColor("#03a81c")

        self._pen_width = 2.4
        self._path_type = path_type

        self._handle_weight = 0.5

        self._hovered = False

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable)

        self.setAcceptHoverEvents(True)

        self._arrow_height = 5
        self._arrow_width = 4

        self._sourceNode = None
        self._destinationNode = None

        self.defaultZValue = 2

        self.path_calc = PathCalc(self._sourcePoint, self._destinationPoint)

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

    def setTheme(self, theme: dict):
        self.setPenWidth(theme['path width'])
        self.setSelectionColor(QtGui.QColor(theme['selection color']))
        self.setHoverColor(QtGui.QColor(theme['selection color']))
        self.setPathColor(QtGui.QColor(theme['path color']))

    def getSourcePoints(self):
        return self._sourcePoint

    def setSourcePoints(self, source: QtCore.QPointF):
        self._sourcePoint = source

    def getDestinationPoints(self):
        return self._destinationPoint

    def setDestinationPoints(self, destination: QtCore.QPointF):
        self._destinationPoint = destination

    def getSourceNode(self):
        return self._sourceNode

    def setSourceNode(self, node):
        self._sourceNode = node

    def getDestinationNode(self):
        return self._destinationNode

    def getDefaultZvalue(self):
        return self.defaultZValue

    def setDestinationNode(self, node):
        self._destinationNode = node

    def setPathType(self, type=DIRECT_PATH):

        if type not in [DIRECT_PATH, BEZIER_PATH, SQUARE_PATH]:
            raise Exception(f"Invalid Path Type: {type}")

        self._path_type = type
        self.update(self.boundingRect().adjusted(50, 50, 50, 50))

    def updatePathPos(self):

        if self._arrow_type == DOUBLE_HEADED:
            source_point = QtCore.QPointF(self._sourceNode.geometry().width() + 2, self._sourceNode.geometry().y() + 10)
            destination_point = QtCore.QPointF(self._destinationNode.geometry().x() - 2, self._destinationNode.geometry().y() + 10)

        else:
            x = self._sourceNode.geometry().width()-self._sourceNode.boundingRect().width()/2
            y = self._sourceNode.geometry().height()+2

            x1 = self._destinationNode.geometry().width()-self._sourceNode.boundingRect().width()/2
            y1 = self._destinationNode.geometry().y()-2
            source_point = QtCore.QPointF(x, y)
            destination_point = QtCore.QPointF(x1, y1)

        self.setSourcePoints(source_point)
        self.setDestinationPoints(destination_point)

    def setSquarePathHandleWeight(self, weight: float):
        self._handle_weight = weight

    def getArrowProperties(self):
        return self._arrow_height, self._arrow_width

    def setArrowProperties(self, height, width):
        self._arrow_height, self._arrow_width = height, width

    def setArrowHead(self, head_type=DESTINATION_HEADED):

        if head_type not in (SOURCE_HEADED, DESTINATION_HEADED, DOUBLE_HEADED):
            raise ValueError(f"Unknown Head type '{head_type}'")

        self._arrow_type = head_type
        self.updatePathPos()

    def removeItem(self):
        self._sourceNode.removePath(self)
        self._destinationNode.removePath(self)
        self.scene().removeItem(self)

    def hoverEnterEvent(self, event) -> None:
        self._hovered = True
        self.update(self.boundingRect().adjusted(50, 50, 50, 50))
        super(Path, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        self._hovered = False
        self.update(self.boundingRect().adjusted(50, 50, 50, 50))
        super(Path, self).hoverLeaveEvent(event)

    def contextMenuEvent(self, event) -> None:

        # if self.isSelected():
        #     return

        menu = QtWidgets.QMenu()

        direct_path = QtWidgets.QAction("Direct Path")
        direct_path.triggered.connect(lambda: self.setPathType(DIRECT_PATH))

        bezier_path = QtWidgets.QAction("Bezier Path")
        bezier_path.triggered.connect(lambda: self.setPathType(BEZIER_PATH))

        square_path = QtWidgets.QAction("Square Path")
        square_path.triggered.connect(lambda: self.setPathType(SQUARE_PATH))

        single_headed = QtWidgets.QAction("Single Head")
        single_headed.triggered.connect(lambda: self.setArrowHead(SOURCE_HEADED))

        double_headed = QtWidgets.QAction("Double Head")
        double_headed.triggered.connect(lambda: self.setArrowHead(DOUBLE_HEADED))

        invert_head = QtWidgets.QAction("Invert Head")
        # invert_head.triggered.connect(lambda: self.setArrowHead(SOURCE_HEADED)
        # if self._arrow_type == DESTINATION_HEADED
        # else self.setArrowHead(DESTINATION_HEADED))
        invert_head.triggered.connect(self.invertArrowHead)

        def setZValue(parent, z: float) -> None:
            parent.setZValue(z)
            parent.defaultZValue = z

        on_top = QtWidgets.QAction("Stay on Top") # places the op_path on top
        on_top.triggered.connect(lambda: setZValue(self, 2))

        at_bottom = QtWidgets.QAction("Move to Bottom")
        at_bottom.triggered.connect(lambda: setZValue(self, -1))

        remove_path = QtWidgets.QAction("Delete Path")
        remove_path.triggered.connect(self.removeItem)

        if self._arrow_type == DOUBLE_HEADED:
            invert_head.setDisabled(True)

        if self.zValue() == 2:
            on_top.setDisabled(True)

        if self.zValue() == -1:
            at_bottom.setDisabled(True)

        menu.addActions([direct_path, bezier_path, square_path])
        menu.addSeparator()
        menu.addActions([single_headed, double_headed, invert_head])
        menu.addSeparator()
        menu.addActions([on_top, at_bottom])
        menu.addSeparator()
        menu.addAction(remove_path)

        menu.exec(event.screenPos())

    def invertArrowHead(self):
        if self._arrow_type == DESTINATION_HEADED:
            self.setArrowHead(SOURCE_HEADED)

        else:
            self.setArrowHead(DESTINATION_HEADED)

        self._sourceNode, self._destinationNode = self._destinationNode, self._sourceNode

    def arrowCalc(self, start_point=None, end_point=None):  # calculates the point where the arrow should be drawn

        try:
            startPoint, endPoint = start_point, end_point

            if start_point is None:
                startPoint = self.getSourcePoints()

            if endPoint is None:
                endPoint = self.getDestinationPoints()

            dx, dy = startPoint.x() - endPoint.x(), startPoint.y() - endPoint.y()

            leng = math.sqrt(dx ** 2 + dy ** 2)
            normX, normY = dx / leng, dy / leng  # normalize

            # perpendicular vector
            perpX = -normY
            perpY = normX

            leftX = endPoint.x() + self._arrow_height * normX + self._arrow_width * perpX
            leftY = endPoint.y() + self._arrow_height * normY + self._arrow_width * perpY

            rightX = endPoint.x() + self._arrow_height * normX - self._arrow_height * perpX
            rightY = endPoint.y() + self._arrow_height * normY - self._arrow_width * perpY

            point2 = QtCore.QPointF(leftX, leftY)
            point3 = QtCore.QPointF(rightX, rightY)

            return QtGui.QPolygonF([point2, endPoint, point3])

        except (ZeroDivisionError, Exception):
            return None

    def calcPath(self):

        self.path_calc.setSource(self.getSourcePoints())
        self.path_calc.setDestiation(self.getDestinationPoints())

        if self._path_type == DIRECT_PATH:
            return self.path_calc.directPath()

        elif self._path_type == BEZIER_PATH:
            return self.path_calc.bezierPath()

        else:
            return self.path_calc.squarePath()

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

        triangle_source = None
        triangle_destination = None

        if self._arrow_type in [DESTINATION_HEADED, DOUBLE_HEADED]:
            triangle_destination = self.arrowCalc(path.pointAtPercent(0.9), self.getDestinationPoints())

        if self._arrow_type in [SOURCE_HEADED, DOUBLE_HEADED]:
            triangle_source = self.arrowCalc(path.pointAtPercent(0.1), self.getSourcePoints())

        if triangle_source is not None:
            painter.drawPolyline(triangle_source)

        if triangle_destination is not None:
            painter.drawPolyline(triangle_destination)

    def serialize(self):
        ordDict = OrderedDict()
        ordDict['source'] = self.getSourceNode().id
        ordDict['destination'] = self.getDestinationNode().id
        ordDict['arrowType'] = self._arrow_type
        ordDict['pathType'] = self._path_type

        return ordDict

    def deserialize(self, data):

        # for item in self.scene().items():
        #
        #     if isinstance(item, ClassNode.ClassNode):
        #         [data['source'], data['destination']]


        self._arrow_type = data['arrowType']
        self._path_type = data['pathType']


class PathCalc:

    def __init__(self, sourcePoints: QtCore.QPointF, destinationPoints: QtCore.QPointF, handle_weight=0.5):
        self._sourcePoint = sourcePoints
        self._destinationPoint = destinationPoints
        self._handle_weight = handle_weight

    def getSourcePoints(self):
        return self._sourcePoint

    def getDestinationPoints(self):
        return self._destinationPoint

    def setSource(self, point: QtCore.QPointF):
        self._sourcePoint = point

    def setDestiation(self, point: QtCore.QPointF):
        self._destinationPoint = point

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
                            (source_y - destination_y) / math.fabs(
                        (source_y - destination_y) if (source_y - destination_y) != 0 else 0.00001
                    )
                    ) * EDGE_ROUNDNESS

            cpy_s = (
                            (destination_y - source_y) / math.fabs(
                        (destination_y - source_y) if (destination_y - source_y) != 0 else 0.00001
                    )
                    ) * EDGE_ROUNDNESS

        path = QtGui.QPainterPath(self.getSourcePoints())

        path.cubicTo(destination_x + cpx_d, destination_y + cpy_d, source_x + cpx_s, source_y + cpy_s,
                     destination_x, destination_y)

        return path

    def squarePath(self):
        s = self.getSourcePoints()
        d = self.getDestinationPoints()

        mid_x = s.x() + ((d.x() - s.x()) * self._handle_weight)

        path = QtGui.QPainterPath(QtCore.QPointF(s.x(), s.y()))
        path.lineTo(mid_x, s.y())
        path.lineTo(mid_x, d.y())
        path.lineTo(d.x(), d.y())

        return path
