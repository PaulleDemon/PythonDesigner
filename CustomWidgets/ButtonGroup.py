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
        self._fixedSize = False

        self.default_btn = None
        self.btn_size = QtCore.QSize()

        try:
            self.group_layout = ButtonGroup.layouts[layout]()

        except KeyError:
            raise ValueError(f"Unknown Layout: {layout}")

        self.setLayout(self.group_layout)

        self.currentSelectedBtn = None

    def addToGroup(self, btn: QtWidgets.QPushButton = None, text: str = '', icon: QtGui.QIcon = QtGui.QIcon(None),
                   **kwargs) -> QtWidgets.QPushButton:

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
        btn.clicked.connect(self.clicked)

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
            self.default_btn = btn
            self.currentSelectedBtn = btn

        if self._fixedSize:
            btn.setFixedSize(self.btn_size)
            btn.setIconSize(QtCore.QSize(self.btn_size.width()-10, self.btn_size.height()-10))

        return btn

    def clicked(self):

        if self.currentSelectedBtn is not None and self.sender():
            self.currentSelectedBtn.setChecked(False)
            self.currentSelectedBtn = None

        if not self.sender().isChecked():
            self.currentSelectedBtn = self.default_btn
            self.default_btn.setChecked(True)
            return

        else:
            self.currentSelectedBtn = self.sender()

        self.currentSelectedBtn.toggled.emit(self.currentSelectedBtn.isChecked())

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
            # print(index)
            while index > 0:
                index -= 1
                btn = self.group_layout.itemAt(index).widget()
                btn.setFixedSize(size)
                btn.setIconSize(QtCore.QSize(size.width() - 10, size.height() - 10))




