from PyQt5 import QtWidgets, Qt


class PageTreeView(QtWidgets.QTreeView):

    def __init__(self, *args, **kwargs):
        super(PageTreeView, self).__init__(*args, **kwargs)

        treeModel = Qt.QStandardItemModel()
        rootNode = treeModel.invisibleRootItem()

        widget = Qt.QStandardItem("Widget")
        second = Qt.QStandardItem("swdwe")
        widget.appendRow(second)
        widget2 = Qt.QStandardItem("erf")

        rootNode.appendRow(widget)
        rootNode.appendRow(widget2)

        self.setModel(treeModel)

    def addRoot(self, name: str):
        pass