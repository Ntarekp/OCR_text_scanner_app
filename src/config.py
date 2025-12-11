import os
import sys

# Tesseract OCR configuration
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Add Tesseract to PATH if not already there
if r'C:\Program Files\Tesseract-OCR' not in os.environ.get('PATH', ''):
    os.environ['PATH'] += os.pathsep + r'C:\Program Files\Tesseract-OCR'

# Verify Tesseract is installed
if not os.path.exists(TESSERACT_CMD):
    print(f"Warning: Tesseract not found at {TESSERACT_CMD}")
    print("Please install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki")

# Configuration settings for the text scanner application

# Default image size for OCR processing
DEFAULT_IMAGE_SIZE = (800, 600)

# Preprocessing settings
PREPROCESSING_SETTINGS = {
    'resize': True,
    'thresholding': True,
    'grayscale': True,
}

# Supported image formats
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

# Default language for OCR
DEFAULT_OCR_LANGUAGE = 'eng'  # Change to desired language code if needed

# Output settings
OUTPUT_TEXT_FILE = 'extracted_text.txt'  # Default output file for extracted text