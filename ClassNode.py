import sys

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtProperty, QObject
from EditableLabel import EditableLabel


class Container(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(Container, self).__init__(*args, **kwargs)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.setSpacing(0)

        # self.title_layout = QtWidgets.QFormLayout()
        # self.body_layout = QtWidgets.QVBoxLayout()

        # layout.addLayout(self.title_layout)
        # layout.addLayout(self.body_layout)
        self.setStyleSheet("background-color: transparent;")

class ClassNode(QtWidgets.QGraphicsItem):

    def __init__(self, *args, **kwargs):
        super(ClassNode, self).__init__(*args, **kwargs)

        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemIsSelectable, True)
        # self.setFlag(self.ItemIsFocusable, True)

        self._title = "None"

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
        # self.proxy = ProxyWidget(self)

        self.proxy.setWidget(self.container)
        self.proxy.setContentsMargins(0, 0, 0, 0)
        self.proxy.setMinimumSize(300, 150)

        self.class_title = EditableLabel("Class Name")
        # self.class_title = QtWidgets.QPushButton("Class Name")
        # self.class_title.clicked.connect(lambda : print("CLICKED PUSH BUTTON"))

        frame = QtWidgets.QFrame()
        frame.setFixedSize(self._title_rect.toRect().width(), self._title_rect.toRect().height())
        title_layout = QtWidgets.QFormLayout(frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.addRow(QtWidgets.QLabel("Class"), self.class_title)
        frame.setStyleSheet("background-color: red;")
        self.container.layout().addStretch(1)
        self._addWidget(frame)

    def _addWidget(self, widget: QtWidgets.QWidget):
        self.container.layout().addWidget(widget)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    def _titleFg(self):
        return self._title_fg

    def _titleBg(self):
        return self._title_bg

    def _bodyFg(self):
        return self._body_fg

    def _bodyBg(self):
        return self._body_bg

    def _borderColor(self):
        return self._border_color

    def _selectionColor(self):
        return self._selection_color

    def _setTitleBg(self, color: QtGui.QColor):
        self._title_bg = color

    def _setTitleFg(self, color: QtGui.QColor):
        self._title_fg = color

    def _setBodyBg(self, color: QtGui.QColor):
        self._body_bg = color

    def _setBodyFg(self, color: QtGui.QColor):
        self._body_fg = color

    def _setborderColor(self, color: QtGui.QColor):
        self._border_color = color

    def _setSelectionColor(self, color: QtGui.QColor):
        self._selection_color = color

    def setTitleRect(self, width, height):
        self._title_rect = QtCore.QRectF(0, 0, width, height)
        self.setBodyHeight()

    def setBodyHeight(self, height: int = -1):

        if height == -1:
            height = self._body_rect.height()

        y, width = self._title_rect.height(), self._title_rect.width()
        self._body_rect = QtCore.QRectF(0, y, width, height)

    TextFg = pyqtProperty(QtGui.QColor, _titleFg, _setTitleFg)
    TextBg = pyqtProperty(QtGui.QColor, _titleBg, _setTitleBg)
    BodyFg = pyqtProperty(QtGui.QColor, _titleFg, _setTitleFg)
    BodyBg = pyqtProperty(QtGui.QColor, _titleBg, _setTitleBg)

    BorderColor = pyqtProperty(QtGui.QColor, _borderColor, _setborderColor)
    SelectionColor = pyqtProperty(QtGui.QColor, _selectionColor, _setSelectionColor)

    # def mousePressEvent(self, event) -> None:
    #
    #     print("FocusWidget: ", self.container.focusWidget())
    #     if isinstance(self.container.focusWidget(), QtWidgets.QLineEdit):
    #         self.container.clearFocus()
    #
    #     super(ClassNode, self).mousePressEvent(event)

    # def sceneEventFilter(self, watched: 'QGraphicsItem', event: QtCore.QEvent) -> bool:

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        print("DOUBLE CLICKED")
        self.proxy.mouseDoubleClickEvent(event)

        super(ClassNode, self).mouseDoubleClickEvent(event)

    def boundingRect(self):
        return self._title_rect.united(self._body_rect)

    def paint(self, painter, option, widget):
        painter.save()

        self._pen.setColor(self._border_color)

        if self.isSelected():
            self._pen.setColor(self._selection_color)

        painter.setPen(self._pen)
        painter.drawRect(self._title_rect.united(self._body_rect).adjusted(-0.7, -0.7, 1, 1))

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._title_bg)
        painter.drawRect(self._title_rect)

        painter.setBrush(self._body_bg)
        painter.drawRect(self._body_rect)

        painter.restore()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    view = QtWidgets.QGraphicsView()
    view.setViewportUpdateMode(view.FullViewportUpdate)

    cls = ClassNode()
    cls.setTitleRect(250, 50)
    cls.setBodyHeight(300)

    scene = QtWidgets.QGraphicsScene()
    scene.addItem(cls)

    view.setScene(scene)
    view.show()

    sys.exit(app.exec())
