def save_image(image, path):
    image.save(path)

def load_image(path):
    from PIL import Image
    return Image.open(path)