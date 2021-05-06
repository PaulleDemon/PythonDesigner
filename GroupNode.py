from PyQt5 import QtWidgets, QtGui, QtCore

from collections import OrderedDict

import ClassNode
from CustomWidgets.EditableLabel import EditableLabel


# todo: deserializing position wrong

class GroupNode(QtWidgets.QGraphicsItem):

    def __init__(self, rect: QtCore.QRectF=QtCore.QRectF(), group_name="Module",*args, **kwargs):
        super(GroupNode, self).__init__(*args, **kwargs)
        self.rect = rect

        self.group_members = set()

        self.id = id(self)

        self.group_name = group_name

        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemIsSelectable, True)
        # self.setFlag(self.ItemIsFocusable, True)

        self.setCacheMode(self.ItemCoordinateCache)

        self.defaultZValue = -3

        self.proxy = QtWidgets.QGraphicsProxyWidget(self)

        self.label = EditableLabel(text=self.group_name)

        self.label.setFixedHeight(30)
        self.label.setStyleSheet("background-color: transparent; color: white;")

        self.proxy.setWidget(self.label)
        # self.proxy.setWidget(widget)
        self.proxy.setContentsMargins(0, 0, 0, 0)
        self.proxy.setFlag(self.proxy.ItemIsFocusable)

    def groupName(self)->str:
        return self.group_name

    def setGroupName(self, name: str):
        self.group_name = name

    def addToGroup(self, item: QtWidgets.QGraphicsItem):
        self.group_members.add(item)
        # item.removed.connect(lambda: self.removeChild(item))  # classNode

    def removeItemFromGroup(self, item: QtWidgets.QGraphicsItem):
        self.group_members.discard(item)

    def removeChild(self, item):
        self.removeItemFromGroup(item)

        if not self.group_members:
            self.scene().removeItem(self)

    def deleteGroup(self, members=False):  # if members is True then children will also get deleted

        if members:
            for item in self.childItems():
                if isinstance(item, QtWidgets.QGraphicsProxyWidget):
                    continue
                item.removeConnectedPaths()

        else:
            for item in self.childItems():

                if isinstance(item, QtWidgets.QGraphicsProxyWidget):
                    continue

                item.setParentItem(None)
                item.removeConnectedPaths()
                item.setPos(item.scenePos())
                self.removeItemFromGroup(item)

        self.scene().views()[0].removeGroup(self)
        # self.scene().removeItem(self)

    # def pos(self) -> QtCore.QPointF:
    #     return self.boundingRect().topLeft()
    #
    # def scenePos(self) -> QtCore.QPointF:
    #     return self.mapToScene(self.boundingRect().topLeft())

    def contextMenuEvent(self, event) -> None:
        menu = QtWidgets.QMenu()

        delete_group = QtWidgets.QAction("Delete Group")
        delete_group.triggered.connect(self.deleteGroup)

        delete_groupMembers = QtWidgets.QAction("Delete Group and Members")
        delete_groupMembers.triggered.connect(lambda: self.deleteGroup(True))

        menu.addActions([delete_group, delete_groupMembers])
        menu.exec(event.screenPos())
    
    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:

        print("Double: ", event.pos(), self.proxy.geometry())
        self.proxy.mouseDoubleClickEvent(event)

        super(GroupNode, self).mouseDoubleClickEvent(event)
    
    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super(GroupNode, self).mousePressEvent(event)
    
    def boundingRect(self):

        self.proxy.setParentItem(None)
        childrenBoundingRect = self.childrenBoundingRect()

        self.proxy.setParentItem(self)
        self.rect = childrenBoundingRect.marginsAdded(QtCore.QMarginsF(20, 50, 20, 20))

        self.proxy.prepareGeometryChange()
        point = QtCore.QPointF(self.rect.center().x()-self.proxy.rect().center().x(), self.rect.y()+10)
        self.proxy.setPos(point)

        return self.rect

    def paint(self, painter: QtGui.QPainter, option, widget):
        painter.setBrush(QtGui.QBrush(QtGui.QColor(128, 125, 125)))

        if self.isSelected():
            painter.setPen(QtGui.QColor("blue"))

        painter.drawRect(self.boundingRect())

    def serialize(self):
        ordDict = OrderedDict()
        ordDict['id'] = self.id
        print("POSition: ", self.pos(), self.scenePos(), self.parentItem(),self.scene())
        ordDict['pos'] = {'x': self.pos().x(), 'y': self.pos().y()}
        ordDict['children'] = [item.id for item in self.childItems() if isinstance(item, ClassNode.ClassNode)]

        # print("Moving...")
        # self.setPos(self.pos().x(), self.pos().y())

        return ordDict

    def deserialize(self, data):
        self.id = data['id']
        print("pos: ", self.mapToScene(data['pos']['x'], data['pos']['y']))
        # self.scenePos().setX(data['pos']['x'])
        # self.scenePos().setY(data['pos']['y'])
        # self.setPos(self.mapToScene(QtCore.QPointF(data['pos']['x'], data['pos']['y'])))
        self.setPos(QtCore.QPointF(data['pos']['x'], data['pos']['y']))
        print("Current pos: ", self.scenePos())
        self.setZValue(self.defaultZValue)

