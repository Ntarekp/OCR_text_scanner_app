import sys
from PyQt5.QtWidgets import QApplication
from gui.window import TextScannerApp

def main():
    app = QApplication(sys.argv)
    window = TextScannerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()