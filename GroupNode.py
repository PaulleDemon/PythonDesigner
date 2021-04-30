from PyQt5 import QtWidgets, QtGui, QtCore

import ClassNode


class GroupNode(QtWidgets.QGraphicsItem):

    def __init__(self, rect: QtCore.QRectF, *args, **kwargs):
        super(GroupNode, self).__init__(*args, **kwargs)
        self.rect = rect

        self.group_members = set()

        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemIsSelectable, True)
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
                self.removeItemFromGroup(item)
                print("Done")

        print("No Problem: ", self.group_members)
        print("children: ", self.childItems())
        self.scene().removeItem(self)
        print()

    def contextMenuEvent(self, event) -> None:
        menu = QtWidgets.QMenu()

        delete_group = QtWidgets.QAction("Delete Group")
        delete_group.triggered.connect(self.deleteGroup)

        delete_groupMembers = QtWidgets.QAction("Delete Group and Members")
        delete_groupMembers.triggered.connect(lambda: self.deleteGroup(True))

        menu.addActions([delete_group, delete_groupMembers])
        menu.exec(event.screenPos())

    # todo: not working as expected

    # def boundingRect(self) -> QtCore.QRectF:
    #     # rect = self.rect
    #     # for item in self.group_members:
    #     #     if isinstance(item, ClassNode.ClassNode):
    #     #         # rect = rect.united(item.boundingRect())
    #     #         rect = QtCore.QRectF(rect.x(), rect.y(), item.boundingRect().width()+rect.x(), item.boundingRect().height()+rect.y())
    #
    #     # self.rect = self.mapToScene(rect).boundingRect().marginsAdded(QtCore.QMarginsF(20, 50, 20, 20)) if rect != QtCore.QRectF(0, 0, 0, 0) else self.rect
    #     # rect = rect.marginsAdded(QtCore.QMarginsF(20, 50, 20, 20))
    #
    #     # self.rect = QtCore.QRectF(self.rect.x(), self.rect.y(), rect.width()+self.rect.x(), rect.height()+self.rect.y())
    #     self.rect = self.childrenBoundingRect().marginsAdded(QtCore.QMarginsF(20, 50, 20, 20))
    #     return self.rect
    
    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super(GroupNode, self).mousePressEvent(event)
    
    def boundingRect(self) -> QtCore.QRectF:
        self.rect = self.childrenBoundingRect().marginsAdded(QtCore.QMarginsF(20, 50, 20, 20))
        return self.rect

    def paint(self, painter: QtGui.QPainter, option, widget):
        painter.setBrush(QtGui.QBrush(QtGui.QColor(128, 125, 125)))

        if self.isSelected():
            painter.setPen(QtGui.QColor("blue"))

        painter.drawRect(self.boundingRect())
