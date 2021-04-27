from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtProperty
from Path import *

class ViewPort(QtWidgets.QGraphicsView):
    
    def __init__(self, *args, **kwargs):
        super(ViewPort, self).__init__(*args, **kwargs)
        self._zoom = 0
        self._isPanning = False
        self._mousePressed = False
        self._isdrawingPath = False

        self._current_path = None

        self._penWidth = 1.2

        self._background_color = QtGui.QColor("#ffffff")
        self._grid_color = QtGui.QColor("#b0b0b0")

        self.setMouseTracking(True)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        self.texture = QtGui.QImage(30, 30, QtGui.QImage.Format_ARGB32)

        self.setViewportUpdateMode(self.FullViewportUpdate)
        self.setDragMode(self.RubberBandDrag)
        # self.setRenderHints(QtGui.QPainter.SmoothPixmapTransform)

        self.setObjectName("View")

    def bgColor(self):
        return self._background_color

    def setBgColor(self, color: QtGui.QColor):
        self._background_color = color
        self.setBackground()

    def gridColor(self):
        return self._grid_color

    def setGridColor(self, color: QtGui.QColor):
        self._grid_color = color
        self.setBackground()

    def penWidth(self):
        return self._penWidth

    def setPenWidth(self, width: float):
        self._penWidth = width
        print("PEN WIDTH: ", width)
        self.setBackground()

    def setBackground(self):
        qp = QtGui.QPainter(self.texture)
        qp.setBrush(self._background_color)
        qp.setPen(QtGui.QPen(self._grid_color, self._penWidth))
        qp.drawRect(self.texture.rect())
        qp.end()
        self.scene().setBackgroundBrush(QtGui.QBrush(self.texture))


    BgColor = pyqtProperty(QtGui.QColor, bgColor, setBgColor)
    GridColor = pyqtProperty(QtGui.QColor, gridColor, setGridColor)
    PenWidth = pyqtProperty(float, penWidth, setPenWidth)

    def setScene(self, scene) -> None:
        super(ViewPort, self).setScene(scene)
        self.setBackground()

    def wheelEvent(self, event: QtGui.QWheelEvent):

        if self.transform().m11() >= 2 or self.transform().m11() < 0.5:
            self.resetTransform()

        if event.angleDelta().y() > 0 and self._zoom <3:
            factor = 1.25
            self._zoom += 1

        elif event.angleDelta().y() < 0 and self._zoom >-2:
            factor = 0.8
            self._zoom -= 1

        else:
            return

        self.scale(factor, factor)

    def mousePressEvent(self, event: QtGui.QMouseEvent):

        if event.button() & QtCore.Qt.LeftButton and event.modifiers() & QtCore.Qt.ControlModifier:
            pos = self.mapToScene(event.pos())
            self._isdrawingPath = True
            # self._current_path = DirectPath(pos, pos)
            # self._current_path = BezierPath(pos, pos)
            self._current_path = SquarePath(source=pos, destination=pos)
            self.scene().addItem(self._current_path)

            return

        if event.button() == QtCore.Qt.LeftButton:
            self._mousePressed = True

            if self._isPanning:
                self.viewport().setCursor(QtCore.Qt.ClosedHandCursor)
                self._dragPos = event.pos()

                event.accept()

            else:
                super().mousePressEvent(event)

        elif event.button() == QtCore.Qt.MidButton:

            self._mousePressed = True
            self._isPanning = True
            self.viewport().setCursor(QtCore.Qt.ClosedHandCursor)
            self._dragPos = event.pos()
            event.accept()
            super(ViewPort, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if self._isdrawingPath:
            pos = self.mapToScene(event.pos())
            self._current_path.setDestinationPoints(pos)
            self.scene().update(self.sceneRect())
            return

        if self._mousePressed and self._isPanning:
            newPos = event.pos()
            diff = newPos - self._dragPos
            self._dragPos = newPos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diff.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diff.y())

            event.accept()
        else:
            super(ViewPort, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        if self._isdrawingPath:
            pos = self.mapToScene(event.pos())
            self._current_path.setDestinationPoints(pos)
            # self.scene().addItem(self._current_path)
            self.scene().update(self.sceneRect())
            self._isdrawingPath = False
            self._current_path = None
            return

        if event.button() == QtCore.Qt.LeftButton:
            if self._isPanning:
                self.viewport().setCursor(QtCore.Qt.OpenHandCursor)
            else:
                self._isPanning = False
                self.viewport().unsetCursor()
            self._mousePressed = False

        elif event.button() == QtCore.Qt.MiddleButton:
            self._isPanning = False
            self.viewport().unsetCursor()

        super(ViewPort, self).mouseReleaseEvent(event)


    # def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
    #     self.fitInView(self.sceneRect().marginsAdded(QtCore.QMarginsF(5, 5, 5, 5)), QtCore.Qt.KeepAspectRatio)
    #     super(ViewPort, self).mouseDoubleClickEvent(event)


class SceneView(QtWidgets.QGraphicsScene):
    pass
