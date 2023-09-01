from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel

class View:
    def __init__(self):
        self.app = QApplication([])
        self.app.setStyle("WindowsVista")
        self.window = QWidget()
        self.window.setWindowTitle("GodPresenter")
        self.window.setMinimumSize(500, 500)
        self.layout = QVBoxLayout()
        self.window.setLayout(self.layout)

        self.add_widgets()
    
    def add_widgets(self):
        self.layout.addWidget(QLabel("GodPresenter"))
    
    def run(self):
        self.window.show()
        self.app.exec()