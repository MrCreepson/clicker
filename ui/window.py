import sys
import subprocess
from PySide6 import QtCore, QtWidgets

class MyWidget(QtWidgets.QWidget):
    def __init__(self, stdout_proxy, config_file, reload_callback=None):
        super().__init__()
        self.stdout = stdout_proxy
        self.config_file = config_file
        self.reload_callback = reload_callback
        self.setWindowTitle("Clicker")
        self.setGeometry(100, 100, 400, 300)

        self.textbox = QtWidgets.QPlainTextEdit("Hello, World!")
        self.textbox.setReadOnly(True)

        self.reload_button = QtWidgets.QPushButton("Reload Settings")
        self.reload_button.clicked.connect(self.on_reload_clicked)

        self.config_button = QtWidgets.QPushButton("Edit Settings")
        self.config_button.clicked.connect(self.on_config_clicked)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.textbox)
        layout.addWidget(self.reload_button)
        layout.addWidget(self.config_button)
        self.setLayout(layout)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_label)
        self.timer.start(100)

    def update_label(self):
        text = self.stdout.getvalue()
        self.textbox.setPlainText(text)

        scrollbar = self.textbox.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_reload_clicked(self):
        self.stdout.write("[*] Reloading settings...\n")
        if self.reload_callback:
            self.reload_callback()

    def on_config_clicked(self):
        subprocess.run(["xdg-open", self.config_file])