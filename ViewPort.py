from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtProperty

import GroupNode
from ClassNode import ClassNode
from Path import *


class ViewPort(QtWidgets.QGraphicsView):

    def __init__(self, *args, **kwargs):
        super(ViewPort, self).__init__(*args, **kwargs)

        self._scene = None

        self._zoom = 0
        self._isPanning = False
        self._mousePressed = False
        self._isdrawingPath = False
        self._isCutting = False
        self._isdrawingGroupRect = False

        self._groupRectangleStartPos = None
        self._groupRectangle = None
        self._groupRectangleBgBrush = QtGui.QBrush(QtGui.QColor(128, 125, 125, 50))

        self._current_path = None
        self._item1 = None
        self._selected_items = set()

        self._line_cutter_painterPath = None  # used to cut paths
        self._line_cutter_path_item = None

        self._penWidth = 1.2

        self._cutter_pen = QtGui.QPen()
        self._cutter_pen.setColor(QtGui.QColor("#000000"))
        self._cutter_pen.setWidthF(1.0)
        self._cutter_pen.setDashPattern([3, 3])

        self._background_color = QtGui.QColor("#ffffff")
        self._grid_color = QtGui.QColor("#b0b0b0")

        self.setMouseTracking(True)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        self.texture = QtGui.QImage(30, 30, QtGui.QImage.Format_ARGB32)

        self.setViewportUpdateMode(self.FullViewportUpdate)
        self.setCacheMode(self.CacheBackground)
        self.setDragMode(self.RubberBandDrag)

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

    def selectionChanged(self):  # moves all the selected items on top

        for item in self._selected_items:
            item.setZValue(item.defaultZValue)

        self._selected_items = set()

        for item in self.scene().selectedItems():

            item.setZValue(item.defaultZValue+1)
            self._selected_items.add(item)

    def setScene(self, scene) -> None:
        super(ViewPort, self).setScene(scene)
        self._scene = scene
        self.setBackground()
        self._scene.selectionChanged.connect(self.selectionChanged)
        self._scene.setItemIndexMethod(self._scene.NoIndex)

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

        pos = self.mapToScene(event.pos())

        if event.button() & QtCore.Qt.LeftButton and event.modifiers() & QtCore.Qt.ShiftModifier:
            item = self._scene.itemAt(pos, QtGui.QTransform())

            if item:
                if isinstance(item, QtWidgets.QGraphicsProxyWidget):
                    item = item.parentItem()

                item.setSelected(True)

            return

        if event.button() & QtCore.Qt.RightButton:
            self._groupRectangle = QtWidgets.QGraphicsRectItem()
            self._groupRectangle.setBrush(self._groupRectangleBgBrush)
            self._scene.addItem(self._groupRectangle)
            self._groupRectangle.setZValue(2)
            self._isdrawingGroupRect = True
            self._groupRectangleStartPos = pos
            return

        if event.button() & QtCore.Qt.LeftButton and event.modifiers() & QtCore.Qt.ControlModifier:

            item = self._scene.itemAt(pos, QtGui.QTransform())
            if item and type(item) == QtWidgets.QGraphicsProxyWidget and isinstance(item.parentItem(), ClassNode):

                self._isdrawingPath = True
                self._current_path = Path(source=pos, destination=pos)
                self._scene.addItem(self._current_path)
                self._item1 = item
                return

        if event.button() & QtCore.Qt.LeftButton and event.modifiers() & QtCore.Qt.AltModifier:
            self._line_cutter_painterPath = QtGui.QPainterPath(pos)
            self._line_cutter_path_item = QtWidgets.QGraphicsPathItem()
            self._line_cutter_path_item.setPen(self._cutter_pen)
            self._scene.addItem(self._line_cutter_path_item)
            self._isCutting = True

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

        pos = self.mapToScene(event.pos())

        if self._isdrawingGroupRect:
            self._groupRectangle.setRect(QtCore.QRectF(self._groupRectangleStartPos, pos))
            return

        if self._isdrawingPath:
            self._current_path.setDestinationPoints(pos)
            self._scene.update(self.sceneRect())
            return

        if self._isCutting:
            self._line_cutter_painterPath.lineTo(pos)
            self._line_cutter_path_item.setPath(self._line_cutter_painterPath)
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

    def removeIntersectingPaths(self):

        def filterInstances(items, instanceOf):
            for _item in items:
                if isinstance(_item, instanceOf):
                    yield _item

        for item in filterInstances(self._line_cutter_path_item.collidingItems(), Path):
            item.removeItem()

    def mouseReleaseEvent(self, event):

        pos = self.mapToScene(event.pos())

        if self._isdrawingGroupRect:

            group = GroupNode.GroupNode(self._groupRectangle.rect())
            colliding_items = self._groupRectangle.collidingItems()

            if colliding_items:
                for item in colliding_items:

                    if type(item) == QtWidgets.QGraphicsProxyWidget and isinstance(item.parentItem(), ClassNode):

                        if isinstance(item, QtWidgets.QGraphicsProxyWidget):
                            item = item.parentItem()

                        item.setParentItem(group)
                        group.addToGroup(item)

                group.setZValue(group.defaultZValue)
                self._scene.addItem(group)

                print("ItemsZ Value: ", [[y.zValue() for y in x.getPaths()] for x in group.childItems()])
            self._scene.removeItem(self._groupRectangle)

            self._groupRectangle = None
            self._isdrawingGroupRect = False
            self._groupRectangleStartPos = None

            return

        if self._isCutting:

            self.removeIntersectingPaths()

            self._scene.removeItem(self._line_cutter_path_item)
            self._line_cutter_painterPath = None
            self._line_cutter_path_item = None
            self._isCutting = False

        if self._isdrawingPath:

            self._current_path.setZValue(-1)
            item = self._scene.itemAt(pos, QtGui.QTransform())

            if item and type(item) == QtWidgets.QGraphicsProxyWidget and isinstance(item.parentItem(), ClassNode) \
                                                                                        and self._item1 != item:

                if isinstance(item, QtWidgets.QGraphicsProxyWidget):
                    item = item.parentItem()

                if isinstance(self._item1, QtWidgets.QGraphicsProxyWidget):
                    self._item1 = self._item1.parentItem()

                if item in self._item1.getDestination():  # remove path if it is already pointing to same destination
                    self._scene.removeItem(self._current_path)

                self._item1.addPath(self._current_path)
                item.addPath(self._current_path)

                self._current_path.setSourceNode(self._item1)
                self._current_path.setDestinationNode(item)
                self._current_path.updatePathPos()
                self._current_path.setZValue(self._current_path.defaultZValue)

            else:
                self._scene.removeItem(self._current_path)

            self._item1 = None
            self._scene.update(self.sceneRect())
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
