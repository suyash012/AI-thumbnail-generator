# filepath: youtube-thumbnail-generator/src/config/settings.py

# Configuration settings for the YouTube thumbnail generator application

import os

class Config:
    IMAGE_SIZE = (1280, 720)  # YouTube thumbnail size
    MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'models', 'enhancement_model')
    STYLE_TRANSFER_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'models', 'style_transfer_model')
    TEMPLATES_PATH = 'data/templates'
    FONTS_PATH = 'data/fonts'
    OUTPUT_PATH = 'output/thumbnails'
    FILTERS = ['blur', 'sharpen', 'brightness']
    DEFAULT_FILTER = 'SHARPEN'
    DEFAULT_FONT = 'arial.ttf'
    
    # YouTube-specific settings
    FACE_ENHANCEMENT_STRENGTH = 1.5
    TEXT_STROKE_WIDTH = 2
    BACKGROUND_BLUR_AMOUNT = 2
    
    # Common YouTube thumbnail text positions
    TEXT_POSITIONS = {
        'top': {'x': 0.5, 'y': 0.2},
        'bottom': {'x': 0.5, 'y': 0.8},
        'center': {'x': 0.5, 'y': 0.5},
        'top_left': {'x': 0.2, 'y': 0.2},
        'top_right': {'x': 0.8, 'y': 0.2},
        'bottom_left': {'x': 0.2, 'y': 0.8},
        'bottom_right': {'x': 0.8, 'y': 0.8}
    }