import sys
from EController import EController
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)

EController().show()

sys.exit(app.exec())
