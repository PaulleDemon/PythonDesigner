import math

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import numpy as np
import sys


class AspectLayout(QLayout):
    def __init__(self, aspect):
        self.aspect = aspect
        self.item = None
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item):
        assert self.item is None, "AspectLayout can contain only 1 widget"
        self.item = item

    def itemAt(self, index):
        if index != 0:
            return None
        if self.item is None:
            return None
        return self.item

    def takeAt(self, index):
        if index != 0:
            return None
        if self.item is None:
            return None
        result = self.item
        self.item = None
        return result

    def setGeometry(self, rect):
        super().setGeometry(rect)
        margins = self.getContentsMargins()
        if self.item is not None:
            availW = rect.width() - margins[1] - margins[3]
            availH = rect.height() - margins[0] - margins[2]
            h = availH
            w = h * self.aspect
            if w > availW:
                x = margins[1]
                w = availW
                h = w/self.aspect
                if self.item.alignment() & Qt.AlignTop:
                    y = margins[0]
                elif self.item.alignment() & Qt.AlignBottom:
                    y = rect.height() - margins[2] - h
                else:
                    y = margins[0] + (availH-h) / 2
            else:
                y = margins[0]
                if self.item.alignment() & Qt.AlignLeft:
                    x = margins[1]
                elif self.item.alignment() & Qt.AlignRight:
                    x = rect.width() - margins[3] - w
                else:
                    x = margins[1] + (availW-w) / 2
            self.item.widget().setGeometry(
                int(rect.x() + x),
                int(rect.y() + y),
                int(w), int(h))

    def sizeHint(self):
        margins = self.getContentsMargins()
        if self.item is None:
            return QSize(margins[0]+margins[2], margins[1]+margins[3])
        s = self.item.sizeHint()
        w, h = s.width(), s.height()
        return QSize(margins[0]+margins[2] + w, margins[1]+margins[3] + h)

    def minimumSize(self):
        margins = self.getContentsMargins()
        if self.item is None:
            return QSize(margins[0]+margins[2], margins[1]+margins[3])
        s = self.item.minimumSize()
        w, h = s.width(), s.height()
        return QSize(margins[0]+margins[2] + w, margins[1]+margins[3] + h)

    def expandingDirections(self):
       return Qt.Horizontal | Qt.Vertical

    def hasHeightForWidth(self):
        return False

    def count(self):
        if self.item is None:
            return 0
        else:
            return 1

    def heightForWidth(self, width):
        margins = self.getContentsMargins()
        height = (width - margins[1] - margins[3]) / self.aspect
        height += margins[0] + margins[2]
        return int(height)


class ColorCircle(QWidget):
    currentColorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None, startupcolor: list = [255, 255, 255], margin=10) -> None:
        super().__init__(parent=parent)

        self.radius = 0
        self.selected_color = QColor(
            startupcolor[0], startupcolor[1], startupcolor[2], 1)
        self.x = 0.5
        self.y = 0.5
        self.h = self.selected_color.hueF()
        self.s = self.selected_color.saturationF()
        self.v = self.selected_color.valueF()
        self.margin = margin

        qsp = QSizePolicy(QSizePolicy.Preferred,
                          QSizePolicy.Preferred)
        qsp.setHeightForWidth(True)
        self.setSizePolicy(qsp)

    def resizeEvent(self, ev: QResizeEvent) -> None:
        self.radius = min([self.width()/2, self.height()/2])

    def paintEvent(self, ev: QPaintEvent) -> None:
        center = QPointF(self.width()/2, self.height()/2)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setViewport(self.margin, self.margin, self.width() -
                      2*self.margin, self.height()-2*self.margin)

        hsv_grad = QConicalGradient(center, 90)
        for deg in range(360):
            col = QColor.fromHsvF(deg / 360, 1, self.v)
            hsv_grad.setColorAt(deg / 360, col)

        val_grad = QRadialGradient(center, self.radius)
        val_grad.setColorAt(0.0, QColor.fromHsvF(0.0, 0.0, self.v, 1.0))
        val_grad.setColorAt(1.0, Qt.transparent)

        p.setPen(Qt.transparent)
        p.setBrush(hsv_grad)
        p.drawEllipse(self.rect())
        p.setBrush(val_grad)
        p.drawEllipse(self.rect())

        p.setViewport(QRect(0, 0, self.width(), self.height()))
        p.setPen(Qt.black)
        p.setBrush(self.selected_color)
        x = self.width()*self.x
        y = self.height()*self.y
        p.drawEllipse(self.line_circle_inter(
            x, y, self.width()/2, self.height()/2, self.radius), 10, 10)

    def recalc(self) -> None:
        self.selected_color.setHsvF(self.h, self.s, self.v)
        self.currentColorChanged.emit(self.selected_color)
        self.repaint()

    def line_circle_inter(self, x: float, y: float, m_x: float, m_y: float, r: float) -> QPointF:
        m = np.array([m_x, m_y])
        p = np.array([x, y])
        d = p - m
        dist = np.linalg.norm(d)
        vec = d/dist
        c = m+vec*r-vec*self.margin
        return QPointF(c[0], c[1]) if dist >= r else QPointF(x, y)

    def map_color(self, x: int, y: int):
        h = (np.arctan2(x-self.radius, y-self.radius)+np.pi)/(2.*np.pi)
        s = np.sqrt(np.power(x-self.radius, 2) +
                    np.power(y-self.radius, 2))/self.radius
        v = self.v
        if s > 1.0:
            s = 1.0
        return h, s, v

    def processMouseEvent(self, ev_x, ev_y) -> None:
        self.h, self.s, self.v = self.map_color(ev_x, ev_y)
        self.x = ev_x / self.width()
        self.y = ev_y / self.height()
        self.recalc()

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        self.processMouseEvent(ev.x(), ev.y())

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.processMouseEvent(ev.x(), ev.y())

    def setHue(self, hue: float) -> None:
        if 0 <= hue <= 1:
            self.h = float(hue)
            self.recalc()
        else:
            raise TypeError("Value must be between 0.0 and 1.0")

    def setSaturation(self, saturation: float) -> None:
        if 0 <= saturation <= 1:
            self.s = float(saturation)
            self.recalc()
        else:
            raise TypeError("Value must be between 0.0 and 1.0")

    def setValue(self, value: float) -> None:
        if 0 <= value <= 1:
            self.v = float(value)
            self.recalc()
        else:
            raise TypeError("Value must be between 0.0 and 1.0")

    def setColor(self, color: QColor) -> None:
        self.h = color.hueF()
        self.s = color.saturationF()
        self.v = color.valueF()
        self.recalc()

    def getHue(self) -> float:
        return self.h

    def getSaturation(self) -> float:
        return self.s

    def getValue(self) -> float:
        return self.v

    def getColor(self) -> QColor:
        return self.selected_color


class ColorCircleDialog(QDialog):
    currentColorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None, width: int = 300, startupcolor: list = [255, 255, 255]) -> None:
        super().__init__(parent=parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.resize(width, width)
        self.setFocusPolicy(Qt.ClickFocus)

        lay = AspectLayout(1)
        self.color_circle = ColorCircle(self, startupcolor=startupcolor)
        self.color_circle.currentColorChanged.connect(self.currentColorChanged.emit)

        lay.addWidget(self.color_circle)

        mainlay = QVBoxLayout()
        mainlay.addLayout(lay)
        fader = QSlider(Qt.Horizontal)
        fader.setMinimum(0)
        fader.setMaximum(255)


        fader.setValue(QColor(*startupcolor).value())
        fader.valueChanged.connect(lambda x: self.color_circle.setValue(x/255))
        self.color_circle.setColor(QColor(*startupcolor))

        hex_validator = QRegExpValidator(QRegExp("^#(?:[0-9a-fA-F]{3}){1,2}$"))

        self.value_edit = LineEdit()
        self.value_edit.setText(QColor(*startupcolor).name())
        self.value_edit.setValidator(hex_validator)
        self.value_edit.textEdited.connect(self.update_wheel)
        self.value_edit.setFocusPolicy(Qt.ClickFocus)
        # self.value_edit.clicked.connect(self.value_edit.clear)

        self.currentColorChanged.connect(self.update_value)

        mainlay.addWidget(fader)
        mainlay.addWidget(self.value_edit)

        self.setLayout(mainlay)

    def update_value(self, color):
        self.value_edit.setText(color.name())

    def update_wheel(self, text):
        if QColor(text).isValid() and len(text) == 7:
            self.color_circle.setColor(QColor(text))

class LineEdit(QLineEdit):

    clicked = pyqtSignal()
    previous = ""

    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()
        super(LineEdit, self).mousePressEvent(QMouseEvent)

    def focusInEvent(self, QFocusEvent):
        self.previous = self.text()
        self.clear()
        super(LineEdit, self).focusInEvent(QFocusEvent)

    def focusOutEvent(self, QFocusEvent):

        if self.text() == "":
            self.setText(self.previous)
        super(LineEdit, self).focusOutEvent(QFocusEvent)

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#
#     window = ColorCircleDialog()
#     window.currentColorChanged.connect(lambda a: print(a.name()))
#     window.show()
#     sys.exit(app.exec_())