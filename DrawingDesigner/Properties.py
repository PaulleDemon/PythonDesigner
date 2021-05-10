from PyQt5 import QtWidgets


class PropertiesPanel(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(PropertiesPanel, self).__init__(*args, **kwargs)

        self.setLayout(QtWidgets.QVBoxLayout())

        self.propertiesTab = QtWidgets.QWidget()
        self.pageTab = QtWidgets.QWidget()
        self.toolProperty = QtWidgets.QWidget()

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.West)

        self.tabs.addTab(self.propertiesTab, "Properties")
        self.tabs.addTab(self.pageTab, "Pages")
        self.tabs.addTab(self.toolProperty, "Tool Properties")

        self.layout().addWidget(self.tabs)