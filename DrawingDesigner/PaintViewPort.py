from PyQt5 import QtWidgets, QtCore, QtGui


# todo: create Widget class to create custom widgets that's where the paint will be used

class ViewPort(QtWidgets.QGraphicsView):

    def __init__(self, *args, **kwargs):
        super(ViewPort, self).__init__(*args, **kwargs)



class CreateWidget(QtWidgets.QGraphicsView):
    pass