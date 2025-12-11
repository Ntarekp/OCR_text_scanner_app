from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, 
    QVBoxLayout, QWidget, QHBoxLayout, QTextEdit, QRubberBand
)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QRect, QPoint, QSize, QTimer
import sys
import cv2
import pytesseract
from config import TESSERACT_CMD
import numpy as np
import os

pytesseract.pytesseract.pytesseract_cmd = TESSERACT_CMD


class ImageLabel(QLabel):
    """Label with ROI selection via mouse drag"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.currentRect = QRect()
        self.selecting = False
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()
            self.selecting = True

    def mouseMoveEvent(self, event):
        if self.selecting:
            rect = QRect(self.origin, event.pos()).normalized()
            self.rubberBand.setGeometry(rect)
            self.currentRect = rect

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.selecting:
            self.selecting = False
            self.rubberBand.hide()

    def get_selection(self):
        return self.currentRect


class TextScannerApp(QMainWindow):
    """Main OCR Scanner Application"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Printed Text Scanner")
        self.setGeometry(100, 100, 1200, 800)
        self.image_path = None
        self.cv_frame = None
        self.capture = None
        self.roi = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_camera_frame)
        self.initUI()

    def initUI(self):
        """Initialize UI components"""
        self.layout = QVBoxLayout()

        # Image display with ROI selection
        self.imageLabel = ImageLabel()
        self.imageLabel.setText("Load an image to scan for text")
        self.imageLabel.setMinimumHeight(350)
        self.imageLabel.setStyleSheet("border: 2px solid black; background-color: #f0f0f0;")
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.imageLabel)

        # Button controls
        buttonsLayout = QHBoxLayout()
        
        self.loadButton = QPushButton("Load Image")
        self.loadButton.clicked.connect(self.loadImage)
        buttonsLayout.addWidget(self.loadButton)

        self.selectROIButton = QPushButton("Select ROI")
        self.selectROIButton.setToolTip("Drag on image to select region, then click this")
        self.selectROIButton.clicked.connect(self._select_roi)
        buttonsLayout.addWidget(self.selectROIButton)

        self.ocrButton = QPushButton("Run OCR")
        self.ocrButton.clicked.connect(self.runOCR)
        buttonsLayout.addWidget(self.ocrButton)

        self.startCamButton = QPushButton("Start Camera")
        self.startCamButton.clicked.connect(self.start_camera)
        buttonsLayout.addWidget(self.startCamButton)

        self.stopCamButton = QPushButton("Stop Camera")
        self.stopCamButton.clicked.connect(self.stop_camera)
        self.stopCamButton.setEnabled(False)
        buttonsLayout.addWidget(self.stopCamButton)
        
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

    # ======================== IMAGE FUNCTIONS ========================

    def loadImage(self):
        """Load image from file dialog"""
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Load Image", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)", 
            options=options
        )
        if fileName:
            self.image_path = fileName
            self.cv_frame = cv2.imread(fileName)
            if self.cv_frame is None:
                self.textEdit.setText("Error: Could not load image.")
                return
            self.roi = None  # Reset ROI on new image
            self._show_frame(self.cv_frame)
            self.textEdit.setText("")

    def _show_frame(self, frame, overlay_boxes=None):
        """Display frame in label with optional text overlay"""
        if frame is None:
            return
            
        display = frame.copy()
        
        # Draw bounding boxes and text
        if overlay_boxes:
            for (x, y, w, h, txt) in overlay_boxes:
                cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(display, txt, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Convert BGR to RGB for PyQt5
        rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytesPerLine = ch * w
        
        qt_img = QImage(rgb.data, w, h, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img).scaledToWidth(600, Qt.SmoothTransformation)

        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.repaint()

    def _select_roi(self):
        """Extract selected ROI from image"""
        if self.cv_frame is None:
            self.textEdit.setText("Error: Please load an image first.")
            return
            
        rect = self.imageLabel.get_selection()
        if rect.isNull():
            self.textEdit.setText("No ROI selected. Drag on image to select a region.")
            return
        
        pixmap = self.imageLabel.pixmap()
        if pixmap is None:
            self.textEdit.setText("No image to crop.")
            return

        # Map displayed coordinates to original image coordinates
        pm_w = pixmap.width()
        pm_h = pixmap.height()
        img_h, img_w = self.cv_frame.shape[:2]

        scale_x = img_w / pm_w
        scale_y = img_h / pm_h

        x = int(rect.left() * scale_x)
        y = int(rect.top() * scale_y)
        w = int(rect.width() * scale_x)
        h = int(rect.height() * scale_y)

        # Clamp to image bounds
        x = max(0, min(x, img_w - 1))
        y = max(0, min(y, img_h - 1))
        w = max(1, min(w, img_w - x))
        h = max(1, min(h, img_h - y))

        self.roi = (x, y, w, h)
        self.textEdit.setText(f"✓ ROI set: x={x}, y={y}, w={w}, h={h}")

    def runOCR(self):
        """Run OCR on image or ROI"""
        if self.cv_frame is None and not self.image_path:
            self.textEdit.setText("Error: Please load an image first.")
            return

        frame = self.cv_frame.copy() if self.cv_frame is not None else cv2.imread(self.image_path)
        
        if frame is None:
            self.textEdit.setText("Error: Could not read image.")
            return

        # Crop to ROI if set
        if self.roi:
            x, y, w, h = self.roi
            crop = frame[y:y+h, x:x+w]
        else:
            crop = frame

        # Preprocessing
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # Extract text
        text = pytesseract.image_to_string(gray)
        self.textEdit.setText(text.strip() if text.strip() else "No text found.")

        # Get bounding boxes for overlay
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        boxes = []

        for i, conf in enumerate(data['conf']):
            try:
                c = float(conf)
            except (ValueError, TypeError):
                continue

            if c > 30:  # Confidence threshold
                x1, y1, w1, h1 = (data['left'][i], data['top'][i], 
                                  data['width'][i], data['height'][i])
                txt = data['text'][i].strip()
                
                if txt:  # Only add non-empty text
                    # Map back to full image if ROI was used
                    if self.roi:
                        rx, ry, _, _ = self.roi
                        boxes.append((rx + x1, ry + y1, w1, h1, txt))
                    else:
                        boxes.append((x1, y1, w1, h1, txt))

        # Show overlayed result
        full = self.cv_frame.copy() if self.cv_frame is not None else cv2.imread(self.image_path)
        if full is not None:
            self._show_frame(full, overlay_boxes=boxes)

    # ======================== CAMERA FUNCTIONS ========================

    def start_camera(self, cam_index=1):
        """Start live camera capture"""
        try:
            if self.capture is None:
                # Use correct VideoCapture syntax for OpenCV 4.x
                self.capture = cv2.VideoCapture(cam_index)
                # Set camera properties
                self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.capture.set(cv2.CAP_PROP_FPS, 30)

            if not self.capture.isOpened():
                self.textEdit.setText("Error: Cannot open camera. Check device.")
                return

            self.startCamButton.setEnabled(False)
            self.stopCamButton.setEnabled(True)
            self.timer.start(30)  # Update every 30ms (~33 FPS)
            self.textEdit.setText("Camera started. Press 'Run OCR' to scan current frame.")
            
        except Exception as e:
            self.textEdit.setText(f"Camera error: {str(e)}")
            self.stop_camera()

    def _update_camera_frame(self):
        """Update frame from camera"""
        if self.capture is None:
            return
            
        ret, frame = self.capture.read()
        if not ret:
            self.textEdit.setText("Error: Cannot read from camera.")
            self.stop_camera()
            return
            
        self.cv_frame = frame
        self._show_frame(frame)

    def stop_camera(self):
        """Stop camera capture"""
        self.timer.stop()
        if self.capture:
            self.capture.release()
            self.capture = None
        self.startCamButton.setEnabled(True)
        self.stopCamButton.setEnabled(False)
        self.textEdit.setText("Camera stopped.")

    def closeEvent(self, event):
        """Cleanup on window close"""
        self.stop_camera()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextScannerApp()
    window.show()
    sys.exit(app.exec_())
