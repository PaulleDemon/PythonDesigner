from PyQt5 import QtWidgets, QtGui, QtCore

import ClassNode


class GroupNode(QtWidgets.QGraphicsItem):

    def __init__(self, rect: QtCore.QRectF, *args, **kwargs):
        super(GroupNode, self).__init__(*args, **kwargs)
        self.rect = rect

        self.group_members = set()

        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemIsSelectable, True)

        self.setCacheMode(self.ItemCoordinateCache)
        # self.setFlag(self.ItemIsFocusable, True)

    def addToGroup(self, item: QtWidgets.QGraphicsItem):
        self.group_members.add(item)

    def removeItemFromGroup(self, item: QtWidgets.QGraphicsItem):
        self.group_members.discard(item)
        print("Group members: ", self.group_members)

    def deleteGroup(self, members=False):  # if members is True then children will also get deleted
        print("Delete Group: ", members)
        if members:
            print("deleting", self.group_members)

            for item in self.childItems():
                print("hello,: ", item)
                item.setParentItem(None)
                # item.setPos(self.mapToScene(item.pos()))
                item.setPos(item.scenePos())
                self.removeItemFromGroup(item)
                print("Done", item.pos(), self.pos())

        self.scene().removeItem(self)
        del self

    def pos(self) -> QtCore.QPointF:
        return QtCore.QPointF(self.rect.x(), self.rect.y())

    def contextMenuEvent(self, event) -> None:
        menu = QtWidgets.QMenu()

        delete_group = QtWidgets.QAction("Delete Group")
        delete_group.triggered.connect(lambda: self.deleteGroup(True))

        delete_groupMembers = QtWidgets.QAction("Delete Group and Members")
        delete_groupMembers.triggered.connect(self.deleteGroup)

        menu.addActions([delete_group, delete_groupMembers])
        menu.exec(event.screenPos())
    
    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super(GroupNode, self).mousePressEvent(event)
    
    def boundingRect(self) -> QtCore.QRectF:
        if self.childrenBoundingRect() == QtCore.QRectF():
            self.scene().removeItem(self)

        self.rect = self.childrenBoundingRect().marginsAdded(QtCore.QMarginsF(20, 50, 20, 20))
        return self.rect

    def paint(self, painter: QtGui.QPainter, option, widget):
        painter.setBrush(QtGui.QBrush(QtGui.QColor(128, 125, 125)))

        if self.isSelected():
            painter.setPen(QtGui.QColor("blue"))

        painter.drawRect(self.boundingRect())
