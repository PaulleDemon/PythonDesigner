from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtProperty
from EditableLabel import EditableLabel, ClassType


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
        self.class_title.enableToolTip("Class Name")
        self.class_title.setValidator()

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

    def addVariableName(self):
        var = ClassType(parent=self, placeHolder="Variable Name")
        var.setValidator()

        var.setText("Variable Name")
        var.setMinimumHeight(30)
        var.deleted.connect(self.adjust)
        self.variable_layout.insertRow(self.variable_layout.count() - 1, var)

    def addMethodName(self):
        var = ClassType(parent=self, placeHolder="Method Name", type=1)
        var.setValidator()

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


class ClassNode(QtWidgets.QGraphicsItem):  # todo: shrink the widget when no widget is there

    def __init__(self, *args, **kwargs):
        super(ClassNode, self).__init__(*args, **kwargs)

        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemIsSelectable, True)
        # self.setFlag(self.ItemIsFocusable, True)

        self._title = "Class: "

        self._border_color = QtGui.QColor("#959596")
        self._selection_color = QtGui.QColor("#6868d4")

        self._pen = QtGui.QPen()
        self._pen.setWidthF(2.8)

        self._title_rect = QtCore.QRectF(0, 0, 100, 30)
        self._body_rect = QtCore.QRectF(0, 30, 100, 100)

        self.path = {}  # stores paths store it in the format {key: path, value: start/end 0 denotes end and 1 denotes start}

        self.InitNode()

    def InitNode(self):

        self.container = Container()
        self.proxy = QtWidgets.QGraphicsProxyWidget(self)

        self.proxy.setWidget(self.container)
        # self.proxy.setMinimumSize(300, 200)
        self.proxy.setContentsMargins(0, 0, 0, 0)

        self.container.setTitle(self._title)
        self.setTitleRect(100, 40)

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

    BorderColor = pyqtProperty(QtGui.QColor, _borderColor, _setborderColor)
    SelectionColor = pyqtProperty(QtGui.QColor, _selectionColor, _setSelectionColor)

    def addPath(self, path, start=False):  # add new path
        self.path[path] = start

    def removePath(self, path):  # remove path
        self.path.pop(path)

    def itemChange(self, change, value):
        # print(f"Change: {change}; value: {value}")
        return super(ClassNode, self).itemChange(change, value)

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.proxy.mouseDoubleClickEvent(event)
        super(ClassNode, self).mouseDoubleClickEvent(event)

    def boundingRect(self):
        return self.proxy.boundingRect()

    def geometry(self):

        pos = self.scenePos()
        # rect = self.mapToParent(self.boundingRect())
        scenepos = self.mapToScene(pos.x() + self.sceneBoundingRect().width(), pos.y() + self.sceneBoundingRect().height())
        x2, y2 = scenepos.x(), scenepos.y()
        # x2 = rect.boundingRect().height() + pos.x()
        # y2 = rect.boundingRect().height() + pos.y()

        print("Width, height: ", x2, y2)
        return QtCore.QRectF(pos, QtCore.QPointF(x2, y2))

    def paint(self, painter, option, widget):
        painter.save()

        self._pen.setColor(self._border_color)

        if self.isSelected():
            self._pen.setColor(self._selection_color)

        painter.setPen(self._pen)
        painter.drawRect(self.boundingRect().adjusted(-1, -1, 1, 1))

        painter.restore()



