# Configuration settings for the text scanner application

# Path to the Tesseract executable
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path as necessary

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