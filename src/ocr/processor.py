from PIL import Image
import pytesseract

class OCRProcessor:
    def __init__(self):
        pass

    def extract_text(self, image_path):
        """Extract text from the given image using PyTesseract."""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

    def extract_text_from_roi(self, image_path, roi):
        """Extract text from a specific region of interest (ROI) in the image."""
        try:
            image = Image.open(image_path)
            cropped_image = image.crop(roi)
            text = pytesseract.image_to_string(cropped_image)
            return text
        except Exception as e:
            print(f"Error processing image ROI: {e}")
            return None

    def supported_image_formats(self):
        """Return a list of supported image formats for OCR."""
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']