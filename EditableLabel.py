from PyQt5 import QtWidgets, QtGui, QtCore


class EditableLabel(QtWidgets.QWidget):
    deleted = QtCore.pyqtSignal()
    textChanged = QtCore.pyqtSignal()

    def __init__(self, text="", placeHolder="class name", *args, **kwargs):
        super(EditableLabel, self).__init__(*args, **kwargs)

        self._text = text

        self.hlayout = QtWidgets.QHBoxLayout(self)
        self.hlayout.setContentsMargins(0, 0, 0, 0)

        self.vlayout = QtWidgets.QVBoxLayout()
        self.vlayout.setContentsMargins(0, 0, 0, 0)

        self._label = QtWidgets.QLabel(text)
        self._label.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)

        self._edit_label = QtWidgets.QLineEdit()
        self._edit_label.textChanged.connect(self._textChanged)
        self._edit_label.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self._edit_label.editingFinished.connect(self.showLabel)
        self._edit_label.setText(text)
        self._edit_label.setPlaceholderText(placeHolder)

        self.vlayout.addWidget(self._label)
        self.vlayout.addWidget(self._edit_label)
        self.showLabel()

        self.hlayout.addLayout(self.vlayout)
        self.setMinimumSize(20, 10)

    def _textChanged(self, text):
        self._text = text
        self.textChanged.emit()

    def showLabel(self):
        self._label.setText(self._edit_label.text())
        self._edit_label.hide()
        self._label.show()

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        menu = QtWidgets.QMenu(self)

        delete_widget = QtWidgets.QAction("Delete", self)
        delete_widget.triggered.connect(self.deleteWidget)

        menu.addAction(delete_widget)
        menu.popup(self.mapToGlobal(event.pos()))

        super(EditableLabel, self).contextMenuEvent(event)

    def deleteWidget(self):
        self.deleteLater()
        self.deleted.emit()

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        if self._label.contentsRect().contains(event.pos()):
            self._label.hide()
            self._edit_label.show()
            self._edit_label.setText(self._label.text())
            self._edit_label.selectAll()
            if self._edit_label.text() == self._text:
                self._edit_label.setText("")

            self._edit_label.setFocus()
            super(EditableLabel, self).mouseDoubleClickEvent(event)

    def setText(self, text):
        self._label.setText(text)
        self._edit_label.setText(text)
        self._text = text

    def getText(self):
        return self._text

    def setValidator(self, regex: str):
        regexp = QtCore.QRegExp(regex)
        validator = QtGui.QRegExpValidator(regexp)
        self._edit_label.setValidator(validator)


class ClassType(EditableLabel):  # class that specifies what type of method, eg: - instance method static method etc.

    _types = {"I": "Instance", "C": "Class", "S": "Static"}
    _member_types = {0: "Variable", 1: "Method"}

    def __init__(self, type=0, text="", placeHolder="class name", *args, **kwargs):
        super(ClassType, self).__init__(text, placeHolder, *args, **kwargs)

        self.member_type = self._member_types[type]
        self.type = "I"

        self.type_lbl = QtWidgets.QLabel(self.type)
        self.hlayout.addWidget(self.type_lbl)

        self.textChanged.connect(self._setTooltip)

        self._setTooltip()

    def _setTooltip(self):
        type_tooltip = f"{self._types[self.type]} {self.member_type}"

        self.type_lbl.setToolTip(type_tooltip)
        self.setToolTip(f"{self.member_type} name: {self.getText()}\n{type_tooltip}")

    def setType(self, type: str):

        if type in self._types.keys():
            self.type = type
            self.type_lbl.setText(type)
            self._setTooltip()

    def setMemberType(self, type: int = 0):
        try:
            self.member_type = self._member_types[type]
        except KeyError:
            pass

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        menu = QtWidgets.QMenu(self)

        delete_widget = QtWidgets.QAction("Delete", self)
        delete_widget.triggered.connect(self.deleteWidget)

        make_instance = QtWidgets.QAction(f"-> Instance {self.member_type}", self)
        make_instance.triggered.connect(lambda: self.setType("I"))

        make_class = QtWidgets.QAction(f"-> Class {self.member_type}", self)
        make_class.triggered.connect(lambda: self.setType("C"))

        make_static = QtWidgets.QAction(f"-> static {self.member_type}", self)
        make_static.triggered.connect(lambda: self.setType("S"))

        menu.addAction(delete_widget)
        menu.addSeparator()
        menu.addActions([make_instance, make_class, make_static])

        menu.popup(self.mapToGlobal(event.pos()))