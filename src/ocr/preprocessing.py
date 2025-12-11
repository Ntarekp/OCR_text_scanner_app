def resize_image(image, width, height):
    from PIL import Image
    return image.resize((width, height), Image.ANTIALIAS)

def convert_to_grayscale(image):
    return image.convert('L')

def apply_threshold(image, threshold=128):
    import numpy as np
    image_array = np.array(image)
    return Image.fromarray((image_array > threshold) * 255).convert('L')

def preprocess_image(image):
    image = convert_to_grayscale(image)
    image = apply_threshold(image)
    return image