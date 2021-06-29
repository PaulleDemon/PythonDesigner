import UndoRedoStack

from Resources import ResourcePaths
from CustomWidgets import ButtonGroup
from DesignerItems import GroupNode
from DesignerItems.ClassNode import ClassNode
from DesignerItems.Path import *

from PyQt5 import QtWidgets

SELECTION_MODE = 0
CONNECT_MODE = 1
CUT_MODE = 2

_style = """
         #View{{
          qproperty-GridColor: {grid_color};
          qproperty-BgColor: {grid_bg_color}; 
          qproperty-PenWidth: {pen_width};
          }}
          
         """


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
        self.path_type = BEZIER_PATH

        self._cutter_pen = QtGui.QPen()
        self._cutter_pen.setColor(QtGui.QColor("#000000"))
        self._cutter_pen.setWidthF(2.0)
        self._cutter_pen.setDashPattern([3, 5])

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

        self.undo_redo = UndoRedoStack.UndoRedoStack()

        self.class_node_theme = {}
        self.path_theme = {}

    def initUI(self):  # initializes tools on the left side (select tool, path tool, cutter tool)

        self.btnGrp = ButtonGroup.ButtonGroup(ButtonGroup.VERTICAL_LAYOUT, parent=self)
        self.btnGrp.setFixedBtnSize(QtCore.QSize(50, 50))
        self.btnGrp.move(QtCore.QPoint(10, 50))
        self.btnGrp_pos = self.btnGrp.geometry().topLeft()

        self.select_btn = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.SELECT_TOOL))
        self.path_btn = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.PATH_TOOL))
        self.cut_path_btn = QtWidgets.QPushButton(icon=QtGui.QIcon(ResourcePaths.PATH_CUTTER))

        # self.select_btn.toggled.connect(lambda: self.changeMode(SELECTION_MODE))
        # self.path_btn.toggled.connect(lambda: self.changeMode(CONNECT_MODE))
        # self.cut_path_btn.toggled.connect(lambda: self.changeMode(CUT_MODE))

        self.btnGrp.addToGroup(self.select_btn, toolTip="Select Tools", checked=True)
        self.btnGrp.addToGroup(self.path_btn, toolTip="Path Tools")
        self.btnGrp.addToGroup(self.cut_path_btn, toolTip="Cut Tools")

        self.btnGrp.toggled.connect(self.changeMode)

    def setTheme(self, theme: dict):

        self.scene_theme = theme["grid"]
        self.class_node_theme = theme["class node"]
        self.path_theme = theme["path"]

        if self.path_theme["path type"] == "Direct":
            self.path_type = DIRECT_PATH

        elif self.path_theme["path type"] == "Bezier":
            self.path_type = BEZIER_PATH

        else:
            self.path_type = SQUARE_PATH

        self._cutter_pen.setWidthF(self.path_theme["cutter width"])
        self._cutter_pen.setColor(QtGui.QColor(self.path_theme["cut color"]))

        self.setStyleSheet(_style.format(grid_color=self.scene_theme['grid_fg'],
                                         grid_bg_color=self.scene_theme['grid_bg'],
                                         pen_width=self.scene_theme['grid_pen_width']
                                         ))

        for item in self.scene().items():
            if isinstance(item, ClassNode):
                item.setTheme(self.class_node_theme)

            elif isinstance(item, Path):
                item.setTheme(self.path_theme)

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

    def setPathType(self, type=BEZIER_PATH):
        self.path_type = type

    def setBackground(self):
        qp = QtGui.QPainter(self.texture)
        qp.setBrush(self._background_color)
        pen = QtGui.QPen(self._grid_color, self._penWidth)
        pen.setCosmetic(True)
        qp.setPen(pen)
        qp.drawRect(self.texture.rect())
        qp.end()
        self.scene().setBackgroundBrush(QtGui.QBrush(self.texture))

    BgColor = pyqtProperty(QtGui.QColor, bgColor, setBgColor)
    GridColor = pyqtProperty(QtGui.QColor, gridColor, setGridColor)
    PenWidth = pyqtProperty(float, penWidth, setPenWidth)

    def changeMode(self, btn: QtWidgets.QPushButton = None, mode: int = None):
        # changes mode (Available modes: Connect mode, selectMode, cut mode)

        if mode is None:
            mode = {self.select_btn: SELECTION_MODE, self.path_btn: CONNECT_MODE, self.cut_path_btn: CUT_MODE}[btn]

        self.current_mode = mode

        if self.current_mode == CONNECT_MODE:
            cursor = QtGui.QCursor(QtGui.QPixmap(ResourcePaths.PATH_TOOL_CURSOR).scaled(30, 30))
            QtWidgets.QApplication.setOverrideCursor(cursor)
            self.setCursor(cursor)

        elif self.current_mode == CUT_MODE:
            cursor = QtGui.QCursor(QtGui.QPixmap(ResourcePaths.PATH_CUTTER_CURSOR).scaled(30, 30))
            QtWidgets.QApplication.setOverrideCursor(cursor)
            self.setCursor(cursor)

        else:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
            self.setCursor(QtCore.Qt.ArrowCursor)

    def selectionChanged(self):  # moves all the selected items on top

        for item in self._selected_items:
            item.setZValue(item.defaultZValue)

        self._selected_items = set()

        for item in self.scene().selectedItems():
            item.setZValue(item.defaultZValue + 1)
            self._selected_items.add(item)

    def toggleToolBar(self):  # animates the tool bar
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

    def removeGroup(self, grp: QtWidgets.QGraphicsItem):  # removes the group from the scene and group variable
        self.scene().removeItem(grp)
        self.groups.discard(grp)

    def addClass(self, pos: QtCore.QPoint):  # adds new class
        node = ClassNode()
        node.setPos(self.mapToScene(pos))
        node.setTheme(self.class_node_theme)
        self._scene.addItem(node)

    def moveToGroup(self, grp):  # moves selected items to group

        selectedItems = self._scene.selectedItems()
        for item in selectedItems:
            if isinstance(item, ClassNode) and not item.parentItem():
                grp.addToGroup(item)

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


class View(ViewPort):

    def setScene(self, scene) -> None:
        super(ViewPort, self).setScene(scene)
        self._scene = scene
        self.setBackground()
        self._scene.selectionChanged.connect(self.selectionChanged)
        self._scene.setItemIndexMethod(self._scene.NoIndex)
        # self._scene.changed.connect(self.registerUndoMove)
        self._scene.sceneChanged.connect(self.registerUndoMove)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):

        menu = QtWidgets.QMenu(self)

        add_class = QtWidgets.QAction("Add Class")
        add_class.triggered.connect(self.registerUndoMove)
        add_class.triggered.connect(lambda: self.addClass(event.pos()))

        items = self._scene.selectedItems()
        itemAt = self._scene.itemAt(self.mapToScene(event.pos()), QtGui.QTransform())

        def removeClassFromGroup(scene):  # removes selected items from group if it in a group
            for item in scene.selectedItems():
                if isinstance(item, ClassNode):
                    item.removeParent()

        add_to_grp = QtWidgets.QMenu("Add to Group")
        remove_from_group = QtWidgets.QAction("Remove from group")
        remove_from_group.triggered.connect(lambda: removeClassFromGroup(self.scene()))

        if itemAt or (len(items) == 1 and not isinstance(items[0], ClassNode)):
            super(ViewPort, self).contextMenuEvent(event)
            return

        if any(isinstance(item, ClassNode) for item in items):

            for grp in self.groups:
                action = QtWidgets.QAction(grp.groupName(), self)
                action.triggered.connect(lambda checked, group=grp: self.moveToGroup(group))
                add_to_grp.addAction(action)

            if not self.groups or not items:
                add_to_grp.setDisabled(True)

        menu.addAction(add_class)
        menu.addMenu(add_to_grp)
        menu.addAction(remove_from_group)

        # menu.exec(self.mapToParent(event.pos()))
        menu.exec(self.mapToGlobal(event.pos()))

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

        if event.modifiers() == QtCore.Qt.ControlModifier and event.button() & QtCore.Qt.RightButton:
            self.registerUndoMove()
            # starts group rectangle
            self._groupRectangle = QtWidgets.QGraphicsRectItem()
            self._groupRectangle.setBrush(self._groupRectangleBgBrush)

            self._scene.addItem(self._groupRectangle)
            self._groupRectangle.setZValue(2)
            self._isdrawingGroupRect = True
            self._groupRectangleStartPos = pos
            return

        if self.current_mode == CONNECT_MODE or (
                event.modifiers() == QtCore.Qt.ControlModifier and event.button() == QtCore.Qt.LeftButton):
            # draws paths
            item = self._scene.itemAt(pos, QtGui.QTransform())
            if item and type(item) == QtWidgets.QGraphicsProxyWidget and isinstance(item.parentItem(), ClassNode):
                self.registerUndoMove()
                self._isdrawingPath = True
                self._current_path = Path(source=pos, destination=pos, path_type=self.path_type)
                self._current_path.setTheme(self.path_theme)
                self._scene.addItem(self._current_path)
                self._item1 = item
                return

        if self.current_mode == CUT_MODE or (
                event.modifiers() == QtCore.Qt.AltModifier and event.button() == QtCore.Qt.LeftButton):
            # draws cut mode
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
                if self.scene().selectedItems():
                    self.registerUndoMove()

                super().mousePressEvent(event)

        elif event.button() == QtCore.Qt.MidButton:  # panning

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

    def removeIntersectingPaths(self):  # removes all the paths over which the cut path is drawn

        def filterInstances(items, instanceOf):
            for _item in items:
                if isinstance(_item, instanceOf):
                    yield _item

        for item in filterInstances(self._line_cutter_path_item.collidingItems(), Path):
            item.removeItem()

    def mouseReleaseEvent(self, event):

        pos = self.mapToScene(event.pos())

        if self._isdrawingGroupRect:

            group = GroupNode.GroupNode(self._groupRectangle.rect(), f"Module {len(self.groups)}")
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

                if not group.childItems() or len(group.childItems()) < 2:
                    self._scene.removeItem(group)
                    self.groups.remove(group)
                    self.undo_redo.pop_undo()  # remove the registered undo move if the rectangle operation fails

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

            else:
                self._scene.removeItem(self._current_path)
                self.undo_redo.pop_undo()  # remove the registered undo move if the path operation fails

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

        elif event.key() == QtCore.Qt.Key_Z and event.modifiers() == QtCore.Qt.ControlModifier:
            self.undoMove()

        elif event.key() == QtCore.Qt.Key_Y and event.modifiers() == QtCore.Qt.ControlModifier:
            self.redoMove()

        else:
            super(ViewPort, self).keyPressEvent(event)

    def clear_scene(self):
        self._selected_items = set()
        # self._scene = QtWidgets.QGraphicsScene()
        self._scene = Scene()
        self.setScene(self._scene)

    def registerUndoMove(self): # registers undo move
        self.undo_redo.add(self.serialize())

    def undoMove(self):

        data = self.undo_redo.undo_move()
        if data:
            self.deSerialize(data)

        else:
            print("no more undo")

    def redoMove(self):
        data = self.undo_redo.redo_move()
        if data:
            self.deSerialize(data)
        else:
            print("no more redo")

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

        return data

    def deSerialize(self, data: dict):  # todo: deserializing groups position doesn't work correctly
        # self._scene = QtWidgets.QGraphicsScene()
        self._scene = Scene()
        self._selected_items = set()
        self.setScene(self._scene)

        import pprint
        pprint.pprint(data.items())

        for nodes in data['ClassNodes']:
            node = ClassNode()
            node.deserialize(nodes)
            node.setTheme(self.class_node_theme)
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
            path.setTheme(self.path_theme)
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

    # def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
    #     self.fitInView(self.sceneRect().marginsAdded(QtCore.QMarginsF(5, 5, 5, 5)), QtCore.Qt.KeepAspectRatio)
    #     super(ViewPort, self).mouseDoubleClickEvent(event)


class Scene(QtWidgets.QGraphicsScene):

    sceneChanged = QtCore.pyqtSignal()

    def addItem(self, item: QtWidgets.QGraphicsObject or QtWidgets.QGraphicsItem) -> None:
        # self.sceneChanged.emit()
        print("Emitting...")
        if isinstance(item, QtWidgets.QGraphicsObject) or issubclass(item.__class__, QtWidgets.QGraphicsObject):
            item.itemChanged.connect(self.sceneChanged.emit)
            print("Emitted>>")
            # item.parentChanged.connect(self.sceneChanged.emit)

        super(Scene, self).addItem(item)
