import os
import sys
import json
import concurrent.futures
from collections import OrderedDict
from PreferenceWindow import Preference

from PyQt5 import QtWidgets

from DesignerItems.ClassNode import ClassNode
from Resources import ResourcePaths
from ViewPort import View, Scene


# todo: undo redo stack, when closing a new file don't ask for saving

class MainWindow(QtWidgets.QMainWindow):
    current_save_file_path = ""

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        self.initMenus()

        self.view = View()
        # self.view.setScene(QtWidgets.QGraphicsScene())
        self.view.setScene(Scene())
        self.setCentralWidget(self.view)

        self.default_file = {}  # this is used to check if the user has made changes to default file
        self.new_file()
        self.statusBar().setVisible(True)

        self.loadViewTheme()

    def initMenus(self):
        self.menu_bar = QtWidgets.QMenuBar(self)

        self.file_menu = QtWidgets.QMenu("File")

        self.new_action = QtWidgets.QAction("New")
        self.new_action.setShortcut("ctrl+N")
        self.new_action.triggered.connect(self.new_file)

        self.open_action = QtWidgets.QAction("Open")
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self.open_file)

        self.save_action = QtWidgets.QAction("Save")
        self.save_action.setShortcut("ctrl+S")
        self.save_action.triggered.connect(self.save_file)

        self.save_as_action = QtWidgets.QAction("Save As")
        self.save_as_action.setShortcut("ctrl+shift+S")
        self.save_as_action.triggered.connect(self.saveAs_file)

        self.quit_action = QtWidgets.QAction("Quit")
        self.quit_action.setShortcut("Ctrl+Q")
        self.quit_action.triggered.connect(self.close)

        self.file_menu.addActions([self.new_action, self.open_action,
                                   self.save_action, self.save_as_action, self.quit_action])

        self.edit_menu = QtWidgets.QMenu("Edit")
        self.preference = QtWidgets.QAction("Preference")
        self.preference.triggered.connect(self.preference_window)

        self.edit_menu.addActions([self.preference])

        self.generate_menu = QtWidgets.QMenu("Generate")

        self.generate_action = QtWidgets.QAction("Generate file")

        self.generate_menu.addActions([self.generate_action])

        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(self.edit_menu)
        self.menu_bar.addMenu(self.generate_menu)

        self.setMenuBar(self.menu_bar)

    def new_file(self):
        self.view.clear_scene()
        self.current_save_file_path = ""
        cls = ClassNode()
        # cls.setTheme()
        self.view.scene().addItem(cls)
        self.default_file = self.view.serialize()

        self.loadViewTheme()

    def closeEvent(self, event) -> None:
        new_data = self.view.serialize()

        show_dialog = False

        if self.current_save_file_path:

            def load():
                with open(self.current_save_file_path, "r") as read:
                    data = OrderedDict(json.load(read))
                return data

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(load)
                old_data = future.result()

            if new_data != old_data:
                print("Not same")
                show_dialog = True

        else:
            if new_data != self.default_file:
                show_dialog = True

        if show_dialog:
            close_dialog = QtWidgets.QMessageBox(parent=self)
            close_dialog.setWindowTitle("Confirm")
            close_dialog.setText("The project has not been saved. Do you wish to save it?")
            close_dialog.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                                            | QtWidgets.QMessageBox.Cancel, )

            val = close_dialog.exec()

            if val == QtWidgets.QMessageBox.Yes:
                saved = self.save_file()
                print("SAVED: ", saved)
                if saved:
                    event.accept()

                else:
                    event.ignore()
                    return

            elif val == QtWidgets.QMessageBox.Cancel:
                event.ignore()
                return

        super(MainWindow, self).closeEvent(event)

    def open_file(self):
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", "",
                                                            "All Files (*);;Designer Files(*.json)",
                                                            "Designer Files(*.json)")
        print(filepath)
        if filepath:
            self.current_save_file_path = filepath

            def load():
                data = ''
                # with open("datafile.json", "r") as read:
                with open(filepath, "r") as read:
                    try:
                        data = OrderedDict(json.load(read))

                    except (json.JSONDecodeError, Exception):
                        print("error loading file")
                        self.statusBar().showMessage(f"Error loading file from '{self.current_save_file_path}'", 3000)

                return data

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(load)
                data = future.result()

            if data:
                try:
                    self.view.deSerialize(data)
                    # self.loadViewTheme()

                except KeyError:
                    self.new_file()
                    print("error loading file")
                    self.statusBar().showMessage(f"Error loading file from '{self.current_save_file_path}'", 3000)

    def save_file(self):  # return True if file is saved
        data = self.view.serialize()

        if self.current_save_file_path:
            def save():
                # with open("datafile.json", "w") as write:
                with open(self.current_save_file_path, "w") as write:
                    json.dump(data, write, indent=2)

                print("Serialize complete.")

            with concurrent.futures.ThreadPoolExecutor() as executor:
                _ = executor.submit(save)

            self.statusBar().showMessage(f"saved to '{self.current_save_file_path}'", 2500)

            return True

        else:
            self.saveAs_file()
            if self.current_save_file_path:
                return True

        return False

    def saveAs_file(self):
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save As", "",
                                                             "All Files (*);;Designer Files(*.json)",
                                                             "Designer Files(*.json)")
        print("Path: ", save_path)
        if save_path:
            self.current_save_file_path = save_path
            self.save_file()

    def loadViewTheme(self):
        with open(os.path.join(ResourcePaths.THEME_PATH_JSON, "theme.json"), 'r') as read:
            theme = json.load(read)

        self.view.setTheme(theme)

    def preference_window(self):
        win = Preference(self)
        win.themeApplied.connect(lambda theme: self.view.setTheme(theme))
        win.exec()


def main():
    app = QtWidgets.QApplication(sys.argv)
    wind = MainWindow()
    wind.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
