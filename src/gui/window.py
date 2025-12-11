from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QTextEdit
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
import sys
import cv2
import pytesseract
from config import TESSERACT_CMD

pytesseract.pytesseract.pytesseract_cmd = TESSERACT_CMD

class TextScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Printed Text Scanner")
        self.setGeometry(100, 100, 1000, 700)
        self.image_path = None
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Image display
        self.imageLabel = QLabel("Load an image to scan for text")
        self.imageLabel.setMinimumHeight(300)
        self.imageLabel.setStyleSheet("border: 1px solid black;")
        self.layout.addWidget(self.imageLabel)

        # Buttons layout
        buttonsLayout = QHBoxLayout()
        
        self.loadButton = QPushButton("Load Image")
        self.loadButton.clicked.connect(self.loadImage)
        buttonsLayout.addWidget(self.loadButton)

        self.ocrButton = QPushButton("Run OCR")
        self.ocrButton.clicked.connect(self.runOCR)
        buttonsLayout.addWidget(self.ocrButton)
        
        self.layout.addLayout(buttonsLayout)

        # Extracted text display
        self.extractedTextLabel = QLabel("Extracted Text:")
        self.layout.addWidget(self.extractedTextLabel)
        
        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setMinimumHeight(200)
        self.layout.addWidget(self.textEdit)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def loadImage(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Load Image", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if fileName:
            self.image_path = fileName
            self.displayImage(fileName)
            self.textEdit.setText("")

    def displayImage(self, filePath):
        pixmap = QPixmap(filePath).scaledToWidth(400, Qt.SmoothTransformation)
        self.imageLabel.setPixmap(pixmap)

    def runOCR(self):
        if not self.image_path:
            self.textEdit.setText("Error: Please load an image first.")
            return
        
        text = self.extractText(self.image_path)
        if text:
            self.textEdit.setText(text)
        else:
            self.textEdit.setText("Error: Could not extract text from image.")

    def extractText(self, image_path):
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)
            return text
        except Exception as e:
            print(f"Error: {e}")
            return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextScannerApp()
    window.show()
    sys.exit(app.exec_())