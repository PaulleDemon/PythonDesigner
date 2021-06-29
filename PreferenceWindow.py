import sys
import os
import json
from PyQt5 import QtWidgets, QtCore, QtGui
from CustomWidgets.ColorPicker import ColorCircleDialog

from Resources import ResourcePaths


class Preference(QtWidgets.QDialog):
    themeApplied = QtCore.pyqtSignal(dict)  # sends signal when preference is changed

    def __init__(self, *args, **kwargs):
        super(Preference, self).__init__(*args, **kwargs)
        self.setModal(True)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.setLayout(QtWidgets.QVBoxLayout())

        formLayout = QtWidgets.QFormLayout()

        pen_width_validator = QtGui.QRegExpValidator(QtCore.QRegExp(r"[1-5]\.[0-9][0-9]"))

        self.pen_width = QtWidgets.QLineEdit()
        self.pen_width.setValidator(pen_width_validator)

        self.pen_color = QtWidgets.QPushButton()
        self.pen_color.clicked.connect(self.colorDialog)

        self.cut_color = QtWidgets.QPushButton()
        self.cut_color.clicked.connect(self.colorDialog)

        cut_color_rgx = QtGui.QRegExpValidator(QtCore.QRegExp(r"[1-5]\.[1-9][1.9]"))
        self.cutter_width = QtWidgets.QLineEdit()
        self.cutter_width.setValidator(cut_color_rgx)

        self.grid_background_color = QtWidgets.QPushButton()
        self.grid_background_color.setAutoFillBackground(True)
        self.grid_background_color.clicked.connect(self.colorDialog)

        self.defalut_path = QtWidgets.QComboBox()
        self.defalut_path.addItems(["Direct", "Bezier", "Square"])

        self.path_width = QtWidgets.QLineEdit()
        self.path_width.setValidator(pen_width_validator)
        self.path_color = QtWidgets.QPushButton(clicked=self.colorDialog)
        self.path_selection_color = QtWidgets.QPushButton(clicked=self.colorDialog)

        self.node_header_fg_color = QtWidgets.QPushButton(clicked=self.colorDialog)
        self.node_header_color = QtWidgets.QPushButton(clicked=self.colorDialog)
        self.node_body_fg_color = QtWidgets.QPushButton(clicked=self.colorDialog)
        self.node_body_color = QtWidgets.QPushButton(clicked=self.colorDialog)
        self.node_selection_color = QtWidgets.QPushButton(clicked=self.colorDialog)
        self.node_border_color = QtWidgets.QPushButton(clicked=self.colorDialog)

        self.theme_options = QtWidgets.QComboBox()
        self.theme_options.addItems(["Dark", "Light"])

        self.apply_btn = QtWidgets.QPushButton("Apply", clicked=self.applyChanges)
        self.ok_btn = QtWidgets.QPushButton("ok", clicked=self.save_changes)
        self.cancel_btn = QtWidgets.QPushButton("Cancel", clicked=self.cancel_changes)

        formLayout.addRow(QtWidgets.QLabel("Grid: "))
        formLayout.addRow("Pen width: ", self.pen_width)
        formLayout.addRow("Grid line color: ", self.pen_color)
        formLayout.addRow("Grid background: ", self.grid_background_color)

        formLayout.addWidget(QtWidgets.QLabel(" "))

        formLayout.addRow(QtWidgets.QLabel("Path: "))
        formLayout.addRow("Default Path: ", self.defalut_path)
        formLayout.addRow("Path color: ", self.path_color)
        formLayout.addRow("Path selection color: ", self.path_selection_color)
        formLayout.addRow("Path width: ", self.path_width)
        formLayout.addRow("Cut path color: ", self.cut_color)
        formLayout.addRow("Cut path width: ", self.cutter_width)

        formLayout.addWidget(QtWidgets.QLabel(" "))

        formLayout.addRow(QtWidgets.QLabel("Node: "))
        formLayout.addRow("Node header foreground: ", self.node_header_fg_color)
        formLayout.addRow("Node header background: ", self.node_header_color)
        formLayout.addRow("Node body foreground: ", self.node_body_fg_color)
        formLayout.addRow("Node body background: ", self.node_body_color)
        formLayout.addRow("Node selection color: ", self.node_selection_color)
        formLayout.addRow("Node border color: ", self.node_border_color)

        formLayout.addWidget(QtWidgets.QLabel(" "))

        formLayout.addRow("Theme", self.theme_options)

        horizontal_layout = QtWidgets.QHBoxLayout()
        horizontal_layout.addStretch(1)
        horizontal_layout.addWidget(self.apply_btn, alignment=QtCore.Qt.AlignRight)
        horizontal_layout.addWidget(self.ok_btn, alignment=QtCore.Qt.AlignRight)
        horizontal_layout.addWidget(self.cancel_btn, alignment=QtCore.Qt.AlignRight)

        self.layout().addLayout(formLayout)
        self.layout().addLayout(horizontal_layout)

        self.load_theme()

    def colorDialog(self):
        widget = self.sender()
        color = widget.palette().button().color()
        self.win = ColorCircleDialog(self, startupcolor=[color.red(), color.green(), color.blue()])
        self.win.currentColorChanged.connect(lambda color: self.changeBtnColor(color, widget))

        pos = self.mapToGlobal(QtCore.QPoint(widget.geometry().center().x(), widget.geometry().bottom()))

        self.win.move(pos)
        self.win.show()

    def changeBtnColor(self, color=None, widget=None, hex=None):
        widget.setStyleSheet(f"background-color: {color.name() if color else hex}; "
                             f"border-radius: 2px; min-height: 25px; border: 2px solid #ffffff")

    def applyChanges(self):
        self.themeApplied.emit(self.getTheme())

    def getTheme(self):
        theme = {
            "grid": {
                "grid_pen_width": float(self.pen_width.text()) if self.pen_width.text() else 1,
                "grid_bg": self.grid_background_color.palette().button().color().name(),
                "grid_fg": self.pen_color.palette().button().color().name()
            },

            "class node": {
                "header_fg": self.node_header_fg_color.palette().button().color().name(),
                "header_bg": self.node_header_color.palette().button().color().name(),
                "body_fg": self.node_body_fg_color.palette().button().color().name(),
                "body_bg": self.node_body_color.palette().button().color().name(),
                "selection_color": self.node_selection_color.palette().button().color().name(),
                "border_color": self.node_border_color.palette().button().color().name()
            },

            "path": {
                "path type": self.defalut_path.currentText(),
                "path color": self.path_color.palette().button().color().name(),
                "selection color": self.path_selection_color.palette().button().color().name(),
                "path width": float(self.path_width.text()) if self.path_width.text() else 1,
                "cut color": self.cut_color.palette().button().color().name(),
                "cutter width": float(self.cutter_width.text()) if self.cutter_width.text() else 1
            }
        }

        return theme

    def cancel_changes(self):
        self.themeApplied.emit(self.theme)
        self.close()

    def save_changes(self):
        # print("Foreground: ", self.node_header_fg_color.palette().button().color().name())
        self.theme = self.getTheme()
        with open(os.path.join(ResourcePaths.THEME_PATH_JSON, "theme.json"), 'w') as write:
            json.dump(self.theme, write, indent=4)

        self.applyChanges()
        self.close()

    def load_theme(self):
        with open(os.path.join(ResourcePaths.THEME_PATH_JSON, "theme.json"), 'r') as read:
            self.theme = json.load(read)

        # print(self.theme)
        grid_theme = self.theme['grid']
        class_node_theme = self.theme['class node']
        path_theme = self.theme['path']

        self.pen_width.setText(f"{grid_theme['grid_pen_width']}")
        self.changeBtnColor(hex=grid_theme['grid_bg'], widget=self.grid_background_color)
        self.changeBtnColor(hex=grid_theme['grid_fg'], widget=self.pen_color)

        self.changeBtnColor(hex=path_theme['path color'], widget=self.path_color)
        self.changeBtnColor(hex=path_theme['selection color'], widget=self.path_selection_color)
        self.path_width.setText(f"{path_theme['path width']}")
        self.defalut_path.setCurrentText(path_theme['path type'])
        self.cutter_width.setText(f"{path_theme['cutter width']}")
        self.changeBtnColor(hex=path_theme['cut color'], widget=self.cut_color)

        self.changeBtnColor(hex=class_node_theme['header_fg'], widget=self.node_header_fg_color)
        self.changeBtnColor(hex=class_node_theme['header_bg'], widget=self.node_header_color)
        self.changeBtnColor(hex=class_node_theme['body_fg'], widget=self.node_body_fg_color)
        self.changeBtnColor(hex=class_node_theme['body_bg'], widget=self.node_body_color)
        self.changeBtnColor(hex=class_node_theme['selection_color'], widget=self.node_selection_color)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    win = Preference()
    win.show()

    sys.exit(app.exec())
