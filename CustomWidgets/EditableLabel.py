import textwrap

from collections import OrderedDict
from PyQt5 import QtWidgets, QtGui, QtCore


class EditableLabel(QtWidgets.QWidget):
    deleted = QtCore.pyqtSignal()
    textChanged = QtCore.pyqtSignal()

    def __init__(self, text="", placeHolder="class name", defaultText:str="", *args, **kwargs):
        super(EditableLabel, self).__init__(*args, **kwargs)

        self._text = text
        self.defaultText = defaultText
        self._toolTipHeading = ""

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
        self._edit_label.setText(self._text) if self._text else self._edit_label.setText(self.defaultText)
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

    def deleteWidget(self):
        self.deleteLater()
        self.deleted.emit()

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent, pos=None):

        pos = event.pos() if self.parent() else self.mapFromParent(event.pos())
        if self._label.geometry().contains(pos):

            self._label.hide()
            self._edit_label.show()
            self._edit_label.setText(self._label.text())
            self._edit_label.selectAll()

            if self._edit_label.text() == self.defaultText:
                self._edit_label.selectAll()

            self._edit_label.setFocus()
            super(EditableLabel, self).mouseDoubleClickEvent(event)

    def setText(self, text):
        self._label.setText(text)
        self._edit_label.setText(text)
        self._text = text

    def getText(self):
        return self._text

    def setValidator(self, regex: str = "^[a-zA-Z_$][a-zA-Z_$0-9]*$"):
        regexp = QtCore.QRegExp(regex)
        validator = QtGui.QRegExpValidator(regexp)
        self._edit_label.setValidator(validator)

    def _updateToolTip(self):
        self._label.setToolTip(f"{self._toolTipHeading}: {textwrap.fill(self.getText(), 15)}")

    def enableToolTip(self, heading=""):
        self._toolTipHeading = heading
        self._edit_label.textChanged.connect(self._updateToolTip)


class ClassType(EditableLabel):  # class that specifies what type of method, eg: - instance method static method etc.

    _types = {"I": "Instance", "C": "Class", "S": "Static"}
    _member_types = {0: "Variable", 1: "Method"}

    def __init__(self, mem_type=0, text="", placeHolder="class name", *args, **kwargs):
        super(ClassType, self).__init__(text, placeHolder, *args, **kwargs)

        self.member_type = self._member_types[mem_type]
        self.type = "I"
        self.comment = ""

        self.type_lbl = QtWidgets.QLabel(self.type)
        self.hlayout.addWidget(self.type_lbl)

        self.textChanged.connect(self._setTooltip)

        self._setTooltip()

    def _setTooltip(self):
        type_tooltip = f"{self._types[self.type]} {self.member_type}"
        widget_tooltip = f"{type_tooltip} name: {self.getText()}"

        if self.comment:
            widget_tooltip += f" \n Comment: \n\t {textwrap.fill(self.comment, 50)}"

        self.type_lbl.setToolTip(type_tooltip)
        self.setToolTip(widget_tooltip)

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

    def addComment(self):
        win = CommentDialog()

        if win.exec():
            self.comment = win.getComment()
            self._setTooltip()

    def removeComment(self):
        self.comment = ""
        self._setTooltip()

    def editComment(self):
        win = CommentDialog(title="Edit Comment")
        win.setComment(self.comment)

        if win.exec():
            self.comment = win.getComment()
            self._setTooltip()

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

        add_comment = QtWidgets.QAction("Add Comment", self)
        add_comment.triggered.connect(self.addComment)

        remove_comment = QtWidgets.QAction("Remove Comment", self)
        remove_comment.triggered.connect(self.removeComment)

        edit_comment = QtWidgets.QAction("Edit Comment", self)
        edit_comment.triggered.connect(self.editComment)

        if not self.comment:
            remove_comment.setDisabled(True)
            edit_comment.setDisabled(True)

        menu.addAction(delete_widget)
        menu.addSeparator()
        menu.addActions([make_instance, make_class, make_static])
        menu.addSeparator()

        menu.addActions([add_comment, remove_comment, edit_comment])

        menu.popup(self.mapToGlobal(event.pos()))

    def serialize(self):
        ordDict = OrderedDict()

        ordDict['text'] = self.getText()
        ordDict['type'] = self.type
        ordDict['memberType'] = self.member_type
        ordDict['comment'] = self.comment

        return ordDict

    def deserialize(self, data):
        self.setText(data['text'])
        self.setType(data['type'])
        self.setMemberType(data['memberType'])
        self.comment = data['comment']
        self._setTooltip()


class CommentDialog(QtWidgets.QDialog):

    def __init__(self, title="Add Comment", *args, **kwargs):
        super(CommentDialog, self).__init__(*args, **kwargs)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setModal(True)
        self.setWindowTitle(title)

        layout = QtWidgets.QGridLayout(self)

        self.textArea = QtWidgets.QTextEdit()
        self.textArea.setPlaceholderText("Type a comment...")
        self.textArea.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)

        ok_btn = QtWidgets.QPushButton("Ok")
        ok_btn.clicked.connect(self.accept)

        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)

        layout.addWidget(self.textArea, 0, 0, 1, 2)
        layout.addWidget(ok_btn, 1, 1)
        layout.addWidget(cancel_btn, 1, 0)

        layout.setAlignment(self.textArea, QtCore.Qt.AlignCenter)
        layout.setAlignment(ok_btn, QtCore.Qt.AlignRight)
        layout.setAlignment(cancel_btn, QtCore.Qt.AlignRight)
        self.setFixedSize(250, 200)

    def getComment(self):
        return self.textArea.toPlainText()

    def setComment(self, text):
        self.textArea.setText(text)
        self.textArea.selectAll()
        self.textArea.moveCursor(QtGui.QTextCursor.End)