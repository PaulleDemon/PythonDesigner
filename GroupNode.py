from PyQt5 import QtWidgets, QtGui, QtCore

from CustomWidgets.EditableLabel import EditableLabel


class GroupNode(QtWidgets.QGraphicsItem):

    def __init__(self, rect: QtCore.QRectF, group_name="Module",*args, **kwargs):
        super(GroupNode, self).__init__(*args, **kwargs)
        self.rect = rect

        self.group_members = set()

        self.group_name = group_name

        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemIsSelectable, True)
        # self.setFlag(self.ItemIsFocusable, True)

        self.setCacheMode(self.ItemCoordinateCache)

        self.defaultZValue = -3

        self.proxy = QtWidgets.QGraphicsProxyWidget(self)

        self.label = EditableLabel(text=self.group_name)

        self.proxy.setWidget(self.label)
        self.proxy.setContentsMargins(0, 0, 0, 0)

        self.label.setFixedHeight(30)
        self.label.setStyleSheet("background-color: red;")

    def groupName(self)->str:
        return self.group_name

    def setGroupName(self, name: str):
        self.group_name = name

    def addToGroup(self, item: QtWidgets.QGraphicsItem):
        self.group_members.add(item)

    def removeItemFromGroup(self, item: QtWidgets.QGraphicsItem):
        self.group_members.discard(item)

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

    def pos(self) -> QtCore.QPointF:
        return QtCore.QPointF(self.rect.x(), self.rect.y())

    def contextMenuEvent(self, event) -> None:
        menu = QtWidgets.QMenu()

        delete_group = QtWidgets.QAction("Delete Group")
        delete_group.triggered.connect(self.deleteGroup)

        delete_groupMembers = QtWidgets.QAction("Delete Group and Members")
        delete_groupMembers.triggered.connect(lambda: self.deleteGroup(True))

        menu.addActions([delete_group, delete_groupMembers])
        menu.exec(event.screenPos())
    
    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.proxy.mouseDoubleClickEvent(event)
        super(GroupNode, self).mouseDoubleClickEvent(event)
    
    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super(GroupNode, self).mousePressEvent(event)
    
    def boundingRect(self) -> QtCore.QRectF:
        if self.childrenBoundingRect() == QtCore.QRectF():
            self.scene().removeItem(self)

        self.rect = self.childrenBoundingRect().marginsAdded(QtCore.QMarginsF(20, 50, 20, 20))
        # self.proxy.setPos(self.proxy.mapFromParent(QtCore.QPointF(self.rect.center().x(), self.rect.y()-10)))

        return self.rect

    def paint(self, painter: QtGui.QPainter, option, widget):
        painter.setBrush(QtGui.QBrush(QtGui.QColor(128, 125, 125)))

        if self.isSelected():
            painter.setPen(QtGui.QColor("blue"))

        painter.drawRect(self.boundingRect())
