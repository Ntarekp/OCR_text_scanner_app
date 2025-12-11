def load_image(image_path):
    from PIL import Image
    return Image.open(image_path)

def save_image(image, save_path):
    image.save(save_path)

def display_image(image, window_title="Image"):
    import matplotlib.pyplot as plt
    plt.imshow(image)
    plt.title(window_title)
    plt.axis('off')
    plt.show()