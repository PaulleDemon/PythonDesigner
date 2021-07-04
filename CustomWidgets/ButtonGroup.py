from PyQt5 import QtWidgets, QtGui, QtCore

VERTICAL_LAYOUT = 0
HORIZONTAL_LAYOUT = 1
GRID_LAYOUT = 2


# store button in a group

class ButtonGroup(QtWidgets.QWidget):
    layouts = {VERTICAL_LAYOUT: QtWidgets.QVBoxLayout, HORIZONTAL_LAYOUT: QtWidgets.QHBoxLayout,
               GRID_LAYOUT: QtWidgets.QGridLayout}

    toggled = QtCore.pyqtSignal(QtWidgets.QPushButton)

    def __init__(self, layout: int = VERTICAL_LAYOUT, *args, **kwargs):
        super(ButtonGroup, self).__init__(*args, **kwargs)

        self.group_layout = None
        self.layout_type = layout

        self.btn_grp = QtWidgets.QButtonGroup()
        self.btn_grp.setExclusive(True)

        self.current_btnIndex = 0
        self.currentSelectedBtn = None

        try:
            self.group_layout = ButtonGroup.layouts[layout]()

        except KeyError:
            raise ValueError(f"Unknown Layout: {layout}")

        self.setLayout(self.group_layout)
        self.btn_grp.buttonClicked.connect(self.clicked)

    def addToGroup(self, btn: QtWidgets.QPushButton = None, text: str = '', icon: QtGui.QIcon = QtGui.QIcon(None),
                   **kwargs) -> QtWidgets.QPushButton:  # adds button to group

        options = {"toolTip": "",
                   "checked": False,
                   "alignment": QtCore.Qt.Alignment(),
                   "row": 0,
                   "column": 0,
                   "rowSpan": 1,
                   "columnSpan": 1
                   }

        if not set(kwargs.keys()).issubset(options.keys()):
            raise ValueError(f"unknown options: {kwargs.keys()} Available options: {options.keys()}")

        options.update(kwargs)

        if btn is None:
            btn = QtWidgets.QPushButton(icon, text)

        btn.setCheckable(True)
        if self.layout_type == GRID_LAYOUT:
            self.group_layout.addWidget(btn, options.pop('row'), options.pop('column'),
                                        options.pop('rowSpan'), options.pop('columnSpan'),
                                        options.pop('alignment'))

        else:
            self.group_layout.addWidget(btn, alignment=options.pop('alignment'))

        if options['toolTip']:
            btn.setToolTip(options.pop("toolTip"))

        if options['checked']:
            btn.setChecked(True)

        if self._fixedSize:
            btn.setFixedSize(self.btn_size)
            btn.setIconSize(QtCore.QSize(self.btn_size.width() - 10, self.btn_size.height() - 10))

        self.btn_grp.addButton(btn)

        return btn

    def clicked(self, btn):
        self.toggled.emit(btn)

    def getCheckedBtn(self):
        return self.btn_grp.checkedButton()

    def setFixedBtnSize(self, size: QtCore.QSize):

        self._fixedSize = True
        self.btn_size = size

        if self.layout_type == GRID_LAYOUT:
            for row in range(1, self.group_layout.rowCount()):
                for col in range(1, self.group_layout.columnCount()):
                    btn = self.group_layout.itemAtPosition(row, col).widget()
                    btn.setFixedSize(size)

        else:
            index = self.group_layout.count()
            while index > 0:
                index -= 1
                btn = self.group_layout.itemAt(index).widget()
                btn.setFixedSize(size)
                btn.setIconSize(QtCore.QSize(size.width() - 10, size.height() - 10))

    def focusNext(self):  # toggles focus

        try:
            self.group_layout.itemAt(self.current_btnIndex).widget().setChecked(False)
            if self.current_btnIndex == self.group_layout.count() - 1:
                self.current_btnIndex = 0
            else:
                self.current_btnIndex += 1

            btn = self.group_layout.itemAt(self.current_btnIndex).widget()
            btn.setChecked(True)
            self.btn_grp.buttonClicked.emit(btn)

        except Exception:
            pass
