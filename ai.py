import os
import argparse
import sys

# Add the project directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Use direct imports instead of youtube_thumbnail_generator prefixes
from src.image_processing.resize import resize_image
from src.image_processing.filters import apply_filter
from src.ai.model import ThumbnailModel
from src.ai.generator import ThumbnailGenerator
from src.utils.file_handler import load_image, save_image
from src.config.settings import Config

def parse_arguments():
    parser = argparse.ArgumentParser(description='YouTube Thumbnail Generator AI Agent')
    parser.add_argument('--input', '-i', required=True, help='Path to input image')
    parser.add_argument('--output', '-o', required=False, help='Path to save output thumbnail')
    parser.add_argument('--filter', '-f', choices=['BLUR', 'CONTOUR', 'DETAIL', 'EDGE_ENHANCE', 'EMBOSS', 'SHARPEN'], 
                        default='SHARPEN', help='Filter to apply to the thumbnail')
    parser.add_argument('--text', '-t', help='Text to overlay on thumbnail')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    print("YouTube Thumbnail Generator AI Agent")
    print(f"Processing image: {args.input}")
    
    # Ensure the output directory exists
    output_path = args.output if args.output else os.path.join(Config.OUTPUT_PATH, 'thumbnail.jpg')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        # Load the input image
        image = load_image(args.input)
        print("Image loaded successfully.")
        
        # Process the image (resize to YouTube thumbnail dimensions)
        print(f"Resizing image to {Config.IMAGE_SIZE}...")
        resized_image = resize_image(image, Config.IMAGE_SIZE)
        
        # Apply filter
        print(f"Applying {args.filter} filter...")
        filtered_image = apply_filter(resized_image, args.filter)
        
        # Initialize the AI model
        print("Loading AI model...")
        model = ThumbnailModel()
        model.load_model()
        
        # Generate thumbnail using AI
        print("Generating thumbnail with AI...")
        generator = ThumbnailGenerator(model)
        thumbnail = generator.generate_thumbnail(filtered_image)
        
        # Add text if provided
        if args.text:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(thumbnail)
            try:
                font = ImageFont.truetype(os.path.join(Config.FONTS_PATH, 'arial.ttf'), 60)
            except IOError:
                font = ImageFont.load_default()
            
            # Position text in the center
            try:
                # For Pillow >= 9.2.0
                text_size = draw.textbbox((0, 0), args.text, font=font)[2:]
                text_width, text_height = text_size
            except AttributeError:
                # For older Pillow versions
                text_width, text_height = draw.textsize(args.text, font=font)
            position = ((Config.IMAGE_SIZE[0] - text_width) // 2, 
                        (Config.IMAGE_SIZE[1] - text_height) // 2)
            
            # Add a shadow/outline to make text more readable
            for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
                draw.text((position[0] + offset[0], position[1] + offset[1]), 
                          args.text, font=font, fill="black")
            
            # Draw the main text
            draw.text(position, args.text, font=font, fill="white")
        
        # Save the generated thumbnail
        print(f"Saving thumbnail to {output_path}...")
        save_image(thumbnail, output_path)
        
        print("Thumbnail generated successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())