# filepath: youtube-thumbnail-generator/src/main.py

from src.image_processing.resize import resize_image
from src.image_processing.filters import apply_filter
from src.ai.model import ThumbnailModel
from src.ai.generator import ThumbnailGenerator
from src.utils.file_handler import load_image, save_image
from src.config.settings import Config

def main():
    # Load the AI model
    model = ThumbnailModel()
    model.load_model()

    # Initialize the thumbnail generator with model
    generator = ThumbnailGenerator(model)

    # Load an image
    input_image_path = 'path/to/input/image.jpg'  # Replace with actual path
    image = load_image(input_image_path)

    # Process the image (resize and apply filter)
    resized_image = resize_image(image, Config.IMAGE_SIZE)
    filtered_image = apply_filter(resized_image, Config.DEFAULT_FILTER)

    # Generate the thumbnail
    thumbnail = generator.generate_thumbnail(filtered_image)

    # Save the generated thumbnail
    save_image(thumbnail, Config.OUTPUT_PATH)

if __name__ == "__main__":
    main()