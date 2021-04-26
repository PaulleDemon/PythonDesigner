import sys

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtProperty
from EditableLabel import EditableLabel


class Container(QtWidgets.QWidget):

    _style = """
            QFrame#TitleFrame{background-color: red;}
            QFrame#Seperator{background-color: black;}
            """

    def __init__(self, title="Class", *args, **kwargs):
        super(Container, self).__init__(*args, **kwargs)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.setSpacing(0)

        self.title_frame = QtWidgets.QFrame()
        self.body_frame = QtWidgets.QFrame()
        self.title_frame.setObjectName("TitleFrame")
        self.body_frame.setObjectName("BodyFrame")

        self.title_layout = QtWidgets.QFormLayout(self.title_frame)
        self.body_layout = QtWidgets.QFormLayout(self.body_frame)

        self.title_layout.setContentsMargins(2, 2, 2, 2)
        self.body_layout.setContentsMargins(2, 2, 2, 2)

        self.class_title = EditableLabel("Class Name")
        self.title = QtWidgets.QLabel(title)
        self.title_layout.addRow(self.title, self.class_title)

        variable_frame = QtWidgets.QFrame()
        method_frame = QtWidgets.QFrame()

        self.variable_layout = QtWidgets.QFormLayout(variable_frame)
        self.method_layout = QtWidgets.QFormLayout(method_frame)

        self.add_variable_btn = QtWidgets.QPushButton("Add Variable")
        self.add_variable_btn.clicked.connect(self.addVariableName)
        self.add_method_btn = QtWidgets.QPushButton("Add Method")
        self.add_method_btn.clicked.connect(self.addMethodName)

        self.variable_layout.addWidget(self.add_variable_btn)
        self.method_layout.addWidget(self.add_method_btn)

        self.vlayout.addWidget(self.title_frame)
        self.vlayout.addWidget(self.body_frame)

        seperator = QtWidgets.QFrame()
        seperator.setObjectName("Seperator")
        seperator.setFrameShape(QtWidgets.QFrame.HLine)

        self.body_layout.addWidget(variable_frame)
        self.body_layout.addWidget(seperator)
        self.body_layout.addWidget(method_frame)

        self.setStyleSheet(self._style)

    def addBody(self, widget):
        self.body_layout.addWidget(widget)

    def setTitleHeight(self, height):
        self.title_frame.setFixedHeight(height)

    def setBodyHeight(self, height):
        self.body_frame.setMinimumHeight(height)

    def addVariableName(self):
        var = EditableLabel(parent=self)
        var.setValidator("^[a-zA-Z_$][a-zA-Z_$0-9]*$")

        var.setText("Variable Name")
        var.setMinimumHeight(30)
        var.deleted.connect(self.adjust)
        self.variable_layout.insertRow(self.variable_layout.count() - 1, var)

    def addMethodName(self):
        var = EditableLabel(parent=self)
        var.setValidator("^[a-zA-Z_$][a-zA-Z_$0-9]*$")

        var.setText("Method Name")
        var.setMinimumHeight(30)
        var.deleted.connect(self.adjust)
        self.method_layout.insertRow(self.method_layout.count() - 1, var)

    def adjust(self):
        QtCore.QTimer.singleShot(10, self.adjustSize)

    def setTitle(self, label: str = ""):
        if not label:
            label = self._title
        self.title.setText(label)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super(Container, self).resizeEvent(a0)
        print("RESIZE: ", self.size())


class ClassNode(QtWidgets.QGraphicsItem):  # todo: shrink the widget when no widget is there

    def __init__(self, *args, **kwargs):
        super(ClassNode, self).__init__(*args, **kwargs)

        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemIsSelectable, True)
        # self.setFlag(self.ItemIsFocusable, True)

        self._title = "Class: "

        self._title_bg = QtGui.QColor("#4b4c4f")
        self._title_fg = QtGui.QColor("#ffffff")
        self._body_bg = QtGui.QColor("#7c7e82")
        self._body_fg = QtGui.QColor("#ffffff")

        self._border_color = QtGui.QColor("#959596")
        self._selection_color = QtGui.QColor("#6868d4")

        self._pen = QtGui.QPen()
        self._pen.setWidthF(2.8)

        self._title_rect = QtCore.QRectF(0, 0, 100, 30)
        self._body_rect = QtCore.QRectF(0, 30, 100, 100)

        self.InitNode()

    def InitNode(self):

        self.container = Container()
        self.proxy = QtWidgets.QGraphicsProxyWidget(self)

        self.proxy.setWidget(self.container)
        # self.proxy.setMinimumSize(300, 200)
        self.proxy.setContentsMargins(0, 0, 0, 0)

        self.container.setTitle(self._title)
        self.setTitleRect(100, 40)
        # self.setBodyHeight(250)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    def _borderColor(self):
        return self._border_color

    def _selectionColor(self):
        return self._selection_color

    def _setborderColor(self, color: QtGui.QColor):
        self._border_color = color

    def _setSelectionColor(self, color: QtGui.QColor):
        self._selection_color = color

    def setTitleRect(self, width, height):
        self.proxy.setMinimumWidth(width)
        self.container.setTitleHeight(height)

    def setBodyHeight(self, height):
        self.container.setBodyHeight(height)

    BorderColor = pyqtProperty(QtGui.QColor, _borderColor, _setborderColor)
    SelectionColor = pyqtProperty(QtGui.QColor, _selectionColor, _setSelectionColor)

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.proxy.mouseDoubleClickEvent(event)
        super(ClassNode, self).mouseDoubleClickEvent(event)

    def boundingRect(self):
        return self.proxy.boundingRect()

    def paint(self, painter, option, widget):
        painter.save()

        self._pen.setColor(self._border_color)

        if self.isSelected():
            self._pen.setColor(self._selection_color)

        painter.setPen(self._pen)
        painter.drawRect(self.boundingRect().adjusted(-1, -1, 1, 1))

        painter.restore()


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    view = QtWidgets.QGraphicsView()
    view.setViewportUpdateMode(view.FullViewportUpdate)

    cls = ClassNode()

    scene = QtWidgets.QGraphicsScene()
    scene.addItem(cls)

    view.setScene(scene)
    view.show()

    sys.exit(app.exec())
