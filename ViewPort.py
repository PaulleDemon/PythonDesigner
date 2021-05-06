import json
import concurrent.futures
from collections import OrderedDict

import ResourcePaths
from CustomWidgets import ButtonGroup
import GroupNode
from ClassNode import ClassNode
from Path import *


SELECTION_MODE = 0
CONNECT_MODE = 1
CUT_MODE = 2


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

        self.groups = set()

        self.current_mode = SELECTION_MODE

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
        self._cutter_pen.setWidthF(2.0)
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
        self.initUI()

    def initUI(self):

        self.btnGrp = ButtonGroup.ButtonGroup(ButtonGroup.VERTICAL_LAYOUT, parent=self)
        self.btnGrp.setFixedBtnSize(QtCore.QSize(50, 50))
        self.btnGrp.move(QtCore.QPoint(10, 50))
        self.btnGrp_pos = self.btnGrp.geometry().topLeft()

        self.select_btn = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.SELECT_TOOL))
        self.path_btn = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.PATH_TOOL))
        self.cut_path_btn = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.PATH_CUTTER))

        self.select_btn.toggled.connect(lambda: self.changeMode(SELECTION_MODE))
        self.path_btn.toggled.connect(lambda: self.changeMode(CONNECT_MODE))
        self.cut_path_btn.toggled.connect(lambda: self.changeMode(CUT_MODE))

        self.btnGrp.addToGroup(self.select_btn, toolTip="Select Tool", checked=True)
        self.btnGrp.addToGroup(self.path_btn, toolTip="Path Tool")
        self.btnGrp.addToGroup(self.cut_path_btn, toolTip="Cut Tool")


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

    def changeMode(self, mode: int):
        self.current_mode = mode
        # self.setCursor(QtGui.QIcon())

        if self.current_mode == CONNECT_MODE:
            cursor = QtGui.QCursor(QtGui.QPixmap(ResourcePaths.PATH_TOOL_CURSOR).scaled(30, 30))
            self.viewport().setCursor(cursor)
            self.setCursor(cursor)

        elif self.current_mode == CUT_MODE:
            cursor = QtGui.QCursor(QtGui.QPixmap(ResourcePaths.PATH_CUTTER_CURSOR).scaled(30, 30))
            self.viewport().setCursor(cursor)
            self.setCursor(cursor)

        else:
            self.viewport().setCursor(QtCore.Qt.ArrowCursor)
            self.setCursor(QtCore.Qt.ArrowCursor)

    def selectionChanged(self):  # moves all the selected items on top

        for item in self._selected_items:
            item.setZValue(item.defaultZValue)

        self._selected_items = set()

        for item in self.scene().selectedItems():
            item.setZValue(item.defaultZValue + 1)
            self._selected_items.add(item)

    def toggleToolBar(self):
        self.anim = QtCore.QPropertyAnimation(self.btnGrp, b"pos")
        self.anim.setDuration(250)

        if self.btnGrp.pos() == self.btnGrp_pos:
            self.anim.setStartValue(self.btnGrp_pos)
            self.anim.setEndValue(QtCore.QPointF(-70, self.btnGrp_pos.y()))

        else:
            self.anim.setStartValue(self.btnGrp.pos())
            self.anim.setEndValue(self.btnGrp_pos)

        # self.anim.finished.connect(lambda: self.btnGrp.hide() if self.btnGrp.visible else self.btnGrp.show())
        self.anim.start(self.anim.DeleteWhenStopped)

    def removeGroup(self, grp: QtWidgets.QGraphicsItem):
        self.scene().removeItem(grp)
        self.groups.discard(grp)

    def addClass(self, pos: QtCore.QPoint):
        node = ClassNode()
        node.setPos(self.mapToScene(pos))

        self._scene.addItem(node)

    def moveToGroup(self, grp):

        selectedItems = self._scene.selectedItems()

        for item in selectedItems:
            if isinstance(item, ClassNode) and not item.parentItem():
                item.setParentItem(grp)
                item.setPos(item.mapToParent(item.pos()))

    def setScene(self, scene) -> None:
        super(ViewPort, self).setScene(scene)
        self._scene = scene
        self.setBackground()
        self._scene.selectionChanged.connect(self.selectionChanged)
        self._scene.setItemIndexMethod(self._scene.NoIndex)

    def wheelEvent(self, event: QtGui.QWheelEvent):

        if self.transform().m11() >= 2 or self.transform().m11() < 0.5:
            self.resetTransform()

        if event.angleDelta().y() > 0 and self._zoom < 3:
            factor = 1.25
            self._zoom += 1

        elif event.angleDelta().y() < 0 and self._zoom > -2:
            factor = 0.8
            self._zoom -= 1

        else:
            return

        self.scale(factor, factor)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):

        menu = QtWidgets.QMenu(self)

        add_class = QtWidgets.QAction("Add Class")
        add_class.triggered.connect(lambda: self.addClass(event.pos()))

        items = self._scene.selectedItems()
        itemAt = self._scene.itemAt(self.mapToScene(event.pos()), QtGui.QTransform())

        add_to_grp = QtWidgets.QMenu("Add to Group")

        if itemAt or len(items) == 1:
            super(ViewPort, self).contextMenuEvent(event)
            return

        if any(isinstance(item, ClassNode) for item in items):

            for grp in self.groups:
                action = QtWidgets.QAction(str(grp), self)
                action.triggered.connect(lambda: self.moveToGroup(grp))
                add_to_grp.addAction(action)

            if not self.groups or not items:
                add_to_grp.setDisabled(True)

        menu.addAction(add_class)
        menu.addMenu(add_to_grp)

        menu.exec(self.mapToParent(event.pos()))


class View(ViewPort):

    def mousePressEvent(self, event: QtGui.QMouseEvent):

        pos = self.mapToScene(event.pos())

        if event.button() & QtCore.Qt.LeftButton and event.modifiers() == QtCore.Qt.ShiftModifier:
            # enables multiple selection using shift
            item = self._scene.itemAt(pos, QtGui.QTransform())

            if item:
                if isinstance(item, QtWidgets.QGraphicsProxyWidget):
                    item = item.parentItem()

                item.setSelected(True)
            return

        if event.modifiers()==QtCore.Qt.ControlModifier and event.button() & QtCore.Qt.RightButton:
            self._groupRectangle = QtWidgets.QGraphicsRectItem()
            self._groupRectangle.setBrush(self._groupRectangleBgBrush)
            self._scene.addItem(self._groupRectangle)
            self._groupRectangle.setZValue(2)
            self._isdrawingGroupRect = True
            self._groupRectangleStartPos = pos
            return

        if self.current_mode == CONNECT_MODE or (event.modifiers() == QtCore.Qt.ControlModifier and event.button() == QtCore.Qt.LeftButton):

            item = self._scene.itemAt(pos, QtGui.QTransform())
            if item and type(item) == QtWidgets.QGraphicsProxyWidget and isinstance(item.parentItem(), ClassNode):
                self._isdrawingPath = True
                self._current_path = Path(source=pos, destination=pos)
                self._scene.addItem(self._current_path)
                self._item1 = item
                return

        if self.current_mode == CUT_MODE or (event.modifiers() == QtCore.Qt.AltModifier and event.button() == QtCore.Qt.LeftButton):
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

                        if isinstance(item.parentItem(), QtWidgets.QGraphicsItem):
                            # continue if the item is already in another group
                            continue

                        item.setParentItem(group)
                        group.addToGroup(item)

                    group.setZValue(group.defaultZValue)
                    self._scene.addItem(group)
                    self.groups.add(group)

                if not group.childItems():
                    self._scene.removeItem(group)
                    self.groups.remove(group)

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

            self._current_path.setZValue(-4)
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
                print("Z VALUE: ", self._current_path.zValue())
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

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:

        if event.key() == QtCore.Qt.Key_T and not self._scene.focusItem():
            self.toggleToolBar()

        elif event.key() == QtCore.Qt.Key_Tab and event.modifiers() == QtCore.Qt.ControlModifier:
            self.btnGrp.focusNext()

        elif event.key() == QtCore.Qt.Key_S and event.modifiers() == QtCore.Qt.ControlModifier:
            self.serialize()

        elif event.key() == QtCore.Qt.Key_O and event.modifiers() == QtCore.Qt.ControlModifier:
            self.deSerialize()

        else:
            super(ViewPort, self).keyPressEvent(event)

    def serialize(self):
        print("Serializing...")
        classNodes = []
        paths = []
        groupNode = []
        for item in self._scene.items():
            if isinstance(item, ClassNode):
                classNodes.append(item.serialize())

            elif isinstance(item, Path):
                paths.append(item.serialize())

            elif isinstance(item, GroupNode.GroupNode):
                groupNode.append(item.serialize())

        data = OrderedDict({"ClassNodes": classNodes,
                            "Paths": paths,
                            "GroupNodes": groupNode})

        def save():
            with open("datafile.json", "w") as write:
                json.dump(data, write, indent=2)

            print("Serialize complete.")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            _ = executor.submit(save)

    def deSerialize(self):

        self._scene = QtWidgets.QGraphicsScene()
        self._selected_items = set()

        self.setScene(self._scene)

        def load():
            with open("datafile.json", "r") as read:
                data = OrderedDict(json.load(read))

            return data

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(load)
            data = future.result()

        # print("Data: ", data)

        for nodes in data['ClassNodes']:
            node = ClassNode()
            node.deserialize(nodes)
            self._scene.addItem(node)

        for grpNodes in data['GroupNodes']:

            groupNode = GroupNode.GroupNode()
            children = grpNodes['children']
            for item in self._scene.items():
                if isinstance(item, ClassNode):
                    if item.id in grpNodes['children']:
                        item.setParentItem(groupNode)
                        children.remove(item.id)

                if not children:
                    break

            groupNode.deserialize(grpNodes)
            self._scene.addItem(groupNode)

        for paths in data['Paths']:
            path = Path()

            for item in self._scene.items():
                if isinstance(item, ClassNode):
                    if item.id == paths['source']:
                        path.setSourceNode(item)
                        item.addPath(path)

                    if item.id == paths['destination']:
                        path.setDestinationNode(item)
                        item.addPath(path)

                if path.getDestinationNode() and path.getSourceNode():
                    path.deserialize(paths)
                    self._scene.addItem(path)
                    break

            # path.deserialize(paths)

# def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
    #     self.fitInView(self.sceneRect().marginsAdded(QtCore.QMarginsF(5, 5, 5, 5)), QtCore.Qt.KeepAspectRatio)
    #     super(ViewPort, self).mouseDoubleClickEvent(event)