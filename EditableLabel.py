from PyQt5 import QtWidgets, QtGui, QtCore


class EditableLabel(QtWidgets.QWidget):

    deleted = QtCore.pyqtSignal()

    def __init__(self, text="", placeHolder="class name", *args, **kwargs):
        super(EditableLabel, self).__init__(*args, **kwargs)

        self.text = text

        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.vlayout.setContentsMargins(0, 0, 0, 0)

        self.label = QtWidgets.QLabel(text)
        self.label.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)

        self.edit_label = QtWidgets.QLineEdit()
        self.edit_label.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.edit_label.editingFinished.connect(self.showLabel)
        self.edit_label.setText(text)
        self.edit_label.setPlaceholderText(placeHolder)

        self.vlayout.addWidget(self.label)
        self.vlayout.addWidget(self.edit_label)
        self.showLabel()

        self.setMinimumSize(20, 10)

    def showLabel(self):
        self.label.setText(self.edit_label.text())
        self.edit_label.hide()
        self.label.show()

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

    def focusOutEvent(self, event):
        print("FOCUS OUT")
        self.showLabel()
        super(EditableLabel, self).focusOutEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        if self.label.contentsRect().contains(event.pos()):
            self.label.hide()
            self.edit_label.show()
            self.edit_label.setText(self.label.text())
            self.edit_label.selectAll()
            print("TExT: ", self.text)
            if self.edit_label.text() == self.text:
                self.edit_label.setText("")

            self.edit_label.setFocus()
            super(EditableLabel, self).mouseDoubleClickEvent(event)

    def setText(self, text):
        self.label.setText(text)
        self.edit_label.setText(text)
        self.text = text

    def getText(self):
        return self.label.text()

    def setValidator(self, regex:str):
        regexp = QtCore.QRegExp(regex)
        validator = QtGui.QRegExpValidator(regexp)
        self.edit_label.setValidator(validator)