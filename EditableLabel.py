from PyQt5 import QtWidgets, QtCore, QtGui


class EditableLabel(QtWidgets.QWidget):

    def __init__(self, text="", placeHolder="class name", *args, **kwargs):
        super(EditableLabel, self).__init__(*args, **kwargs)

        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.vlayout.setContentsMargins(0, 0, 0, 0)

        self.label = QtWidgets.QLabel(text)
        self.label.setStyleSheet("background-color: yellow;")

        self.edit_label = QtWidgets.QLineEdit()
        self.edit_label.setStyleSheet("background-color: blue;")
        self.edit_label.editingFinished.connect(self.showLabel)
        self.edit_label.setText(text)
        self.edit_label.setPlaceholderText(placeHolder)

        self.vlayout.addWidget(self.label)
        self.vlayout.addWidget(self.edit_label)
        self.showLabel()

    def showLabel(self):
        print("Show Label")
        self.label.setText(self.edit_label.text())
        self.edit_label.hide()
        self.label.show()

    def mouseDoubleClickEvent(self, event):
        print("CLICKED")
        self.label.hide()
        self.edit_label.show()
        self.edit_label.setText(self.label.text())
        super(EditableLabel, self).mouseDoubleClickEvent(event)
