def resize_image(image, size):
    from PIL import Image
    resized_image = image.resize(size, Image.LANCZOS)
    return resized_image