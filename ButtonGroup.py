import sys
from PyQt5 import QtWidgets, QtGui, QtCore

VERTICAL_LAYOUT = 0
HORIZONTAL_LAYOUT = 1
GRID_LAYOUT = 2


class ButtonGroup(QtWidgets.QWidget):

    layouts = {VERTICAL_LAYOUT: QtWidgets.QVBoxLayout, HORIZONTAL_LAYOUT: QtWidgets.QHBoxLayout,
               GRID_LAYOUT: QtWidgets.QGridLayout}

    def __init__(self, layout: int = VERTICAL_LAYOUT, *args, **kwargs):
        super(ButtonGroup, self).__init__(*args, **kwargs)

        self.group_layout = None
        self.layout_type = layout

        try:
            self.group_layout = ButtonGroup.layouts[layout]()

        except KeyError:
            raise ValueError(f"Unknown Layout: {layout}")

        self.setLayout(self.group_layout)

        self.currentSelectedBtn = None

    def addToGroup(self, btn: QtWidgets.QPushButton = None, text='', icon=QtGui.QIcon(None), **kwargs):

        options = {'alignment': QtCore.Qt.Alignment(),
                   'row': 0,
                   'column': 0,
                   'rowSpan':1,
                   'columnSpan': 1
                   }

        if not set(kwargs.keys()).issubset(options.keys()):
            raise ValueError(f"unknown options: {kwargs.keys()} Available options: {options.keys()}")

        options.update(kwargs)

        if btn is None:
            btn = QtWidgets.QPushButton(icon, text)

        btn.setCheckable(True)
        btn.toggled.connect(self.toggled)

        if self.layout_type == GRID_LAYOUT:
            self.group_layout.add(btn).addItem(btn, options.pop('row'), options.pop('column'),
                                               options.pop('rowSpan'), options.pop('columnspan'),
                                               options.pop('alignment'))

        else:
            self.group_layout.addWidget(btn, alignment=options.pop('alignment'))


    def toggled(self):

        if self.currentSelectedBtn is not None:
            self.currentSelectedBtn.setChecked(False)

        self.currentSelectedBtn = self.sender()


def main():
    if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)

        btn = ButtonGroup(VERTICAL_LAYOUT)

        btn.addToGroup(text="Hello")
        btn.addToGroup(text="Bye2")
        btn.addToGroup(text="Bye3")
        btn.addToGroup(text="Bye4")

        btn.show()

        sys.exit(app.exec())


if __name__ == '__main__':
    main()
