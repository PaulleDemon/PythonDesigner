import copy
import os

import pathlib, shutil
import json
import sys
import threading
from PyQt5 import QtWidgets, QtCore


class PythonFileGenerator(QtWidgets.QDialog):

    def __init__(self, path, *args, **kwargs):
        super(PythonFileGenerator, self).__init__(*args, **kwargs)
        self.setWindowTitle("Generate")
        self.setModal(True)

        self.op_path = ""
        self.src_path = path

        grid_layout = QtWidgets.QGridLayout(self)
        grid_layout.setSpacing(20)

        self.error_label = QtWidgets.QLabel("")

        self.output_path = QtWidgets.QLineEdit()
        self.select_folder_btn = QtWidgets.QPushButton("folder", clicked=self.select_folder)
        self.select_folder_btn.setMaximumWidth(100)

        self.project_name_lbl = QtWidgets.QLabel("Project name")
        self.project_name_lbl.setMaximumWidth(100)

        self.project_name = QtWidgets.QLineEdit()

        self.ok_btn = QtWidgets.QPushButton("Generate", clicked=self.generate)
        self.cancel_btn = QtWidgets.QPushButton("Cancel", clicked=self.close)

        grid_layout.addWidget(self.error_label, 0, 0)
        grid_layout.addWidget(QtWidgets.QLabel("Select ouput folder"), 1, 0)
        grid_layout.addWidget(self.output_path, 2, 0)
        grid_layout.addWidget(self.select_folder_btn, 2, 1)

        hbox_layout = QtWidgets.QHBoxLayout()
        hbox_layout.addWidget(self.project_name_lbl)
        hbox_layout.addWidget(self.project_name)

        grid_layout.addLayout(hbox_layout, 3, 0, 1, 2)

        hbox_layout2 = QtWidgets.QHBoxLayout()
        hbox_layout2.addStretch(1)
        hbox_layout2.addWidget(self.ok_btn)
        hbox_layout2.addWidget(self.cancel_btn)

        grid_layout.addLayout(hbox_layout2, 4, 0, 1, 2)

    def select_folder(self):
        file_path = QtWidgets.QFileDialog.getExistingDirectory(self, "select op_path")
        self.output_path.setText(file_path)

    def check_valid_path(self, text):

        if not os.path.isdir(text):
            self.error_label.setText("Invalid op_path")
            return False

        return True

    def generate(self):

        if not self.check_valid_path(self.output_path.text()):
            return

        if not self.project_name.text():
            self.error_label.setText("Enter project name")
            return

        else:
            self.error_label.setText("")
            self.op_path = os.path.join(self.output_path.text(), self.project_name.text())
            # self.accept()

            removed = self.removeFiles()

            if removed:
                msg = QtWidgets.QMessageBox(self)
                msg.setWindowTitle("ERROR")
                msg.setIcon(msg.Critical)
                msg.setText(f"{removed}")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.buttonClicked.connect(msg.close)

                msg.exec()

            new_file = GenerateFile(self.src_path, self.op_path)
            new_file.finshedGenerating.connect(self.completedGenerating)
            new_file.generate()
            self.startProgressBar()


            print("GENERATING")

    def getPath(self):
        return self.op_path

    def startProgressBar(self):

        self.progress_window = QtWidgets.QProgressDialog(self)

        self.progress_window.setLayout(QtWidgets.QVBoxLayout())
        lbl = QtWidgets.QLabel("Generating please wait")
        self.progress_window.layout().addWidget(lbl)

        self.progress_window.setRange(0, 0)
        self.progress_window.exec()

    def completedGenerating(self):
        self.progress_window.close()
        self.close()

    def removeFiles(self):
        if os.path.exists(self.op_path):
            for path in pathlib.Path(self.op_path).iterdir():
                try:
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        shutil.rmtree(path)

                except PermissionError as e:
                    return e


class GenerateFile(QtCore.QObject):

    finshedGenerating = QtCore.pyqtSignal()

    def __init__(self, data_path, destination_path):
        super(GenerateFile, self).__init__()

        if not os.path.exists(destination_path):
            os.mkdir(destination_path)

        self.data = {}
        self.data_path = data_path
        self.destination_path = destination_path

    def generate(self):

        thread = threading.Thread(target=self._generate)
        thread.setDaemon(True)
        thread.start()

    def _generate(self):  # generates the python file

        with open(self.data_path, 'r') as read:
            self.data = json.load(read)

        classnodes = self.data['ClassNodes']
        groupnodes = self.data['GroupNodes']
        paths = self.data['Paths']

        clsnode_cpy = copy.deepcopy(classnodes)

        for items in groupnodes:
            full_path = self.createDir(items['groupName'])

            if not full_path:
                continue

            else:

                for child in copy.deepcopy(items['children']):
                    for x in clsnode_cpy:

                        if child == x['id']:

                            # classnodes.remove(x)
                            classnodes = [cls for cls in classnodes if cls['id'] != child]

                            container = x['container']

                            cls_name = ''.join(container['className'])
                            create_file = self.create_python_file(os.path.join(full_path, cls_name))

                            if not create_file:
                                continue

                            with open(create_file, 'w') as write:
                                class_name = ''.join(container['className'].split())

                                inherit = "Object"
                                for var in copy.deepcopy(paths):
                                    print(var['destination'])
                                    if var['arrowType'] not in [0, 1]:
                                        continue

                                    if var['destination'] == child:
                                        for c in clsnode_cpy:
                                            if c['id'] == var['source']:
                                                inherit = c['container']['className']
                                                inherit = "".join(inherit.split())

                                                write.write(f"\nfrom {inherit} import {inherit}\n")
                                                paths.remove(var)
                                                break

                                write.write(f"\nclass {class_name}({inherit}):\n")

                                if not container['variables'] and not container['methods']:
                                    write.write("\tpass\n")
                                    continue

                                for var in copy.deepcopy(container['variables']):
                                    if var['type'] == 'C':
                                        var_name = ''.join(var['text'].split())
                                        write.write(f"\n\t{var_name} = None")
                                        container['variables'].remove(var)

                                if container['variables']:
                                    write.write('\n\n\tdef __init__(*args, **kwargs):\n')

                                for var in container['variables']:
                                    var_name = ''.join(var['text'].split())
                                    write.write(f"\n\t\tself.{var_name} = None")

                                for var in container['methods']:
                                    memb_name = ''.join(var['text'].split())
                                    write.write("\n\n\t")
                                    if var['type'] == 'I':
                                        write.write(f"\n\tdef {memb_name}(self):")
                                        write.write(f"\n\t\tpass")

                                    elif var['type'] == 'C':
                                        write.write("@classmethod")
                                        write.write(f"\n\tdef {memb_name}(cls):")
                                        write.write(f"\n\t\tpass")

                                    else:
                                        write.write("@staticmethod")
                                        write.write(f"\n\tdef {memb_name}():")
                                        write.write(f"\n\t\tpass")


        print("Running...2", classnodes)
        for x in classnodes:

            container = x['container']
            class_name = ''.join(container['className'].split())
            create_file = self.create_python_file(class_name)

            if not create_file:
                continue

            with open(create_file, 'w') as write:

                inherit = "Object"
                for var in paths:
                    print(var['destination'])
                    if var['arrowType'] not in [0, 1]:
                        continue

                    if var['destination'] == x['id']:
                        for c in classnodes:
                            if c['id'] == var['source']:
                                inherit = c['container']['className']
                                inherit = "".join(inherit.split())

                                write.write(f"\nfrom {inherit} import {inherit}\n")

                                break

                write.write(f"\nclass {class_name}({inherit}):\n")

                if not container['variables'] and not container['methods']:
                    write.write("\tpass\n")
                    continue

                for var in copy.deepcopy(container['variables']):
                    if var['type'] == 'C':
                        var_name = ''.join(var['text'].split())
                        write.write(f"\n\t{var_name} = None")
                        container['variables'].remove(var)

                if container['variables']:
                    write.write('\n\n\tdef __init__(*args, **kwargs):\n')

                for var in container['variables']:
                    var_name = ''.join(var['text'].split())
                    write.write(f"\n\t\tself.{var_name} = None")

                for var in container['methods']:
                    memb_name = ''.join(var['text'].split())
                    write.write("\n\n\t")
                    if var['type'] == 'I':
                        write.write(f"\n\tdef {memb_name}(self):")
                        write.write(f"\n\t\tpass")

                    elif var['type'] == 'C':
                        write.write("@classmethod")
                        write.write(f"\n\tdef {memb_name}(cls):")
                        write.write(f"\n\t\tpass")

                    else:
                        write.write("@staticmethod")
                        write.write(f"\n\tdef {memb_name}():")
                        write.write(f"\n\t\tpass")

        self.finshedGenerating.emit()

                            # classnodes.remove(child)

    def createDir(self, dir):
        path = os.path.join(self.destination_path, dir)

        try:
            pathlib.Path(path).mkdir()
            return path

        except FileExistsError:
            return False

    def create_python_file(self, filename):

        filename = filename[0].lower() + filename[1:] + '.py'

        path = os.path.join(self.destination_path, filename)

        if not os.path.exists(path):
            with open(path, 'w'):
                pass

            return path

        return False


# step 1: create group nodes
# step 2: create class nodes
# step 3: link paths


# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#
#     win = PythonFileGenerator(r"C:/Users/Paul/Desktop/random.json")
#     win.exec()
#     sys.exit(app.exit())
