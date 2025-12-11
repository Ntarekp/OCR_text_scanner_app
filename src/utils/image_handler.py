from PIL import Image
import matplotlib.pyplot as plt


def load_image(image_path):
    """
    Load an image using PIL.
    Returns a PIL.Image object.
    """
    return Image.open(image_path)


def save_image(image, save_path):
    """
    Save a PIL image to disk.
    """
    image.save(save_path)


def display_image(image, window_title="Image"):
    """
    Display an image using matplotlib.
    """
    plt.imshow(image)
    plt.title(window_title)
    plt.axis('off')
    plt.show()
