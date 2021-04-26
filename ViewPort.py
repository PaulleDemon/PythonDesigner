from PyQt5 import QtWidgets


class ViewPort(QtWidgets.QGraphicsScene):
    
    def __init__(self, *args, **kwargs):
        super(ViewPort, self).__init__(*args, **kwargs)
