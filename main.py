import sys

from PyQt5 import QtWidgets

from DesignerItems.ClassNode import ClassNode
from ViewPort import View


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()



def main():
    app = QtWidgets.QApplication(sys.argv)

    view = View()
    # view.setStyleSheet("#View{qproperty-GridColor: #615e5e; qproperty-BgColor: #c4c4c4; qproperty-PenWidth: 1.2;}")

    cls = ClassNode()
    cls2 = ClassNode()
    cls3 = ClassNode()
    # path = DirectPath()

    scene = QtWidgets.QGraphicsScene()
    scene.addItem(cls)
    scene.addItem(cls2)
    scene.addItem(cls3)
    # scene.addItem(path)

    view.setScene(scene)
    view.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
