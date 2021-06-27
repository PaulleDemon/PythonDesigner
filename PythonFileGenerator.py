import os
from PyQt5 import QtWidgets


class PythonFileGenerator(QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        super(PythonFileGenerator, self).__init__(*args, **kwargs)

        form_layout = QtWidgets.QFormLayout(self)

        self.error_label = QtWidgets.QLabel("")

        self.output_path = QtWidgets.QLineEdit()
        self.select_folder_btn = QtWidgets.QPushButton("folder", clicked=self.select_folder)

        self.project_name = QtWidgets.QLineEdit()

        self.ok_btn = QtWidgets.QPushButton("Generate")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

        form_layout.addRow(self.error_label)
        form_layout.addRow(QtWidgets.QLabel("Select ouput folder"))
        form_layout.addRow(self.output_path, self.select_folder_btn)
        form_layout.addRow(QtWidgets.QLabel("Project name"), self.project_name)
        form_layout.addRow(self.ok_btn, self.cancel_btn)

    def select_folder(self):
        file_path = QtWidgets.QFileDialog.getExistingDirectory(self, "select path")
        self.output_path.setText(file_path)

    def check_valid_path(self, text):

        if not os.path.isdir(text):
            self.error_label.setText("Invalid path")
            return False

        return True

    def generate(self):

        if not self.check_valid_path(self.output_path.text()):
            return


def generate_file(serialize_data, output_path):
    pass