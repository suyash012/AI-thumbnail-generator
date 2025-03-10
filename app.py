import os
from flask import Flask, request, render_template, send_from_directory, url_for, redirect, jsonify
import uuid
import re  # Add this import
from src.image_processing.resize import resize_image
from src.image_processing.filters import apply_filter
from src.ai.model import ThumbnailModel
from src.ai.generator import ThumbnailGenerator
from src.utils.file_handler import load_image, save_image
from src.config.settings import Config
import cv2
import json
import base64
import io
import numpy as np
from PIL import ImageDraw, Image
from src.ai.prompt_engine import PromptEngine
from datetime import datetime
from src.utils.database import ThumbnailDatabase

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output/thumbnails'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Initialize the AI model (do this once at startup to avoid reloading)
model = ThumbnailModel()
model.load_model()
generator = ThumbnailGenerator(model)

# Initialize the prompt engine alongside your model
prompt_engine = PromptEngine()

# Initialize the database
thumbnail_db = ThumbnailDatabase()


def allowed_file(filename):
    """Check if uploaded file has an allowed extension"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate_thumbnail():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Generate a unique filename to avoid collisions
        unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(upload_path)
        
        # Get filter and text from form
        filter_type = request.form.get('filter', 'SHARPEN')
        thumbnail_text = request.form.get('text', '')
        
        # Get prompt from form
        user_prompt = request.form.get('prompt', '')
        
        # Process the prompt if provided
        thumbnail_properties = {}
        if user_prompt:
            thumbnail_properties = prompt_engine.analyze_prompt(user_prompt)
            print(f"Analyzed prompt: {json.dumps(thumbnail_properties, indent=2)}")
        
        try:
            # Process the image
            image = load_image(upload_path)
            resized_image = resize_image(image, Config.IMAGE_SIZE)
            
            # Use filter from prompt if available, otherwise use form input
            if thumbnail_properties and "style" in thumbnail_properties:
                if thumbnail_properties["style"] == "gaming":
                    filter_type = "SHARPEN"
                elif thumbnail_properties["style"] == "vlog":
                    filter_type = "EDGE_ENHANCE"
                elif thumbnail_properties["style"] == "tutorial":
                    filter_type = "DETAIL"
                else:
                    filter_type = request.form.get('filter', 'SHARPEN')
            else:
                filter_type = request.form.get('filter', 'SHARPEN')
                
            filtered_image = apply_filter(resized_image, filter_type)
            
            # Generate thumbnail using AI
            thumbnail = generator.generate_thumbnail(filtered_image, thumbnail_properties)
            
            # Add text from prompt if available, otherwise use form input
            text_overlay = ""
            if thumbnail_properties and thumbnail_properties["text_overlay"]:
                text_overlay = thumbnail_properties["text_overlay"]
            else:
                text_overlay = request.form.get('text', '')
            
            # Add text if provided
            if text_overlay:
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(thumbnail)
                try:
                    # First try our own font
                    font_path = os.path.join(Config.FONTS_PATH, 'arial.ttf')
                    if os.path.exists(font_path) and os.path.getsize(font_path) > 0:
                        font = ImageFont.truetype(font_path, 60)
                    else:
                        # Try system fonts
                        system_fonts = [
                            'Arial.ttf',
                            'DejaVuSans.ttf',
                            'FreeSans.ttf',
                            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                            'C:\\Windows\\Fonts\\arial.ttf'
                        ]
                        font = None
                        for font_name in system_fonts:
                            try:
                                font = ImageFont.truetype(font_name, 60)
                                break
                            except:
                                continue
                                
                        if font is None:
                            font = ImageFont.load_default()
                except:
                    font = ImageFont.load_default()
                
                # Get text size
                try:
                    # For Pillow >= 9.2.0
                    text_size = draw.textbbox((0, 0), text_overlay, font=font)[2:]
                    text_width, text_height = text_size
                except AttributeError:
                    # For older Pillow versions
                    text_width, text_height = draw.textsize(text_overlay, font=font)
                
                # Position text in the center
                position = ((Config.IMAGE_SIZE[0] - text_width) // 2, 
                            (Config.IMAGE_SIZE[1] - text_height) // 2)
                
                # Add a shadow/outline to make text more readable
                for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
                    draw.text((position[0] + offset[0], position[1] + offset[1]), 
                            text_overlay, font=font, fill="black")
                
                # Draw the main text
                draw.text(position, text_overlay, font=font, fill="white")
            
            # Save the generated thumbnail
            output_filename = f'thumbnail_{unique_filename}'
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            save_image(thumbnail, output_path)
            
            # Return results page
            return render_template('result.html', 
                                original_image=f'/uploads/{unique_filename}',
                                thumbnail_image=f'/thumbnails/{output_filename}')
            
        except Exception as e:
            return render_template('error.html', error=str(e))
    
    return redirect(url_for('index'))


@app.route('/generate-from-prompt', methods=['POST'])
def generate_from_prompt():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    prompt = request.form.get('prompt', '')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    if file and allowed_file(file.filename):
        # Generate a unique filename to avoid collisions
        unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(upload_path)
        
        try:
            # Process the prompt
            thumbnail_properties = prompt_engine.analyze_prompt(prompt)
            
            print(f"\n\n===== THUMBNAIL GENERATION PLAN =====")
            print(f"Style: {thumbnail_properties['style']}")
            print(f"Tone: {thumbnail_properties['tone']}")
            print(f"Colors: {', '.join(thumbnail_properties['color_scheme'])}") 
            print(f"Visual Elements: {', '.join(thumbnail_properties['visual_elements'])}")
            print(f"Text: {thumbnail_properties['text_overlay']}")
            print(f"Background Removal: {thumbnail_properties.get('remove_background', False)}")
            print(f"===================================\n\n")
            
            # Load and process the image
            image = load_image(upload_path)
            resized_image = resize_image(image.convert('RGB'), Config.IMAGE_SIZE)
            
            # Generate thumbnail using AI with prompt properties
            # Note: the background removal and positioning will be handled by the generator
            thumbnail = generator.generate_thumbnail(resized_image, thumbnail_properties)
            
            # Save the generated thumbnail
            output_filename = f'ai_thumbnail_{unique_filename}'
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            save_image(thumbnail, output_path)
            
            # Save to database
            thumbnail_id = str(uuid.uuid4())
            thumbnail_db.save_thumbnail(
                thumbnail_id=thumbnail_id,
                original_path=f'/uploads/{unique_filename}',
                thumbnail_path=f'/thumbnails/{output_filename}',
                prompt=prompt,
                properties=thumbnail_properties
            )
            
            # Return the paths and thumbnail ID
            return jsonify({
                'success': True,
                'thumbnail_id': thumbnail_id,
                'original_image': f'/uploads/{unique_filename}',
                'thumbnail_image': f'/thumbnails/{output_filename}',
                'properties': thumbnail_properties
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/analyze', methods=['POST'])
def analyze_image():
    from PIL import ImageDraw
    import numpy as np

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Save the file temporarily
        unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(upload_path)
        
        try:
            # Process the image
            image = load_image(upload_path)
            
            # Create content analyzer
            from src.ai.content_analyzer import ContentAnalyzer
            analyzer = ContentAnalyzer()
            
            # Analyze image
            content_info = analyzer.analyze(image)
            
            # Convert numpy arrays to lists for JSON serialization
            faces = content_info['faces'].tolist() if isinstance(content_info['faces'], np.ndarray) else []
            
            # Generate a preview with face boxes
            preview_img = image.copy()
            draw = ImageDraw.Draw(preview_img)
            
            for (x, y, w, h) in faces:
                draw.rectangle([x, y, x+w, y+h], outline="red", width=3)
            
            # Convert image to base64 for sending to client
            buffered = io.BytesIO()
            preview_img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Return analysis results and preview
            return jsonify({
                'faces_detected': len(faces),
                'optimal_text_placement': content_info['text_regions'][0],
                'brightness_level': float(content_info['brightness']),
                'contrast_level': float(content_info['contrast']),
                'preview_image': f'data:image/jpeg;base64,{img_str}'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/thumbnails/<filename>')
def thumbnail_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)


@app.route('/ai-prompt')
def ai_prompt_interface():
    return render_template('ai_prompt.html')


@app.route('/feedback', methods=['POST'])
def thumbnail_feedback():
    data = request.json
    thumbnail_id = data.get('thumbnail_id')
    rating = data.get('rating')
    feedback_text = data.get('feedback')
    
    # Save feedback to database
    thumbnail_db.save_feedback(
        thumbnail_id=thumbnail_id,
        rating=rating,
        feedback_text=feedback_text
    )
    
    print(f"Received feedback for thumbnail {thumbnail_id}: rating={rating}")
    
    return jsonify({'success': True})


# Add this new route

@app.route('/enhance-prompt', methods=['POST'])
def enhance_prompt():
    data = request.json
    basic_prompt = data.get('prompt', '')
    
    if not basic_prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    try:
        # Extract the intention from the basic prompt
        style_keywords = {
            "gaming": ["game", "gaming", "stream", "play"],
            "vlog": ["vlog", "daily", "lifestyle", "travel"],
            "tutorial": ["how to", "tutorial", "guide", "learn"],
            "reaction": ["reaction", "react", "watching"],
            "review": ["review", "opinion", "thoughts"]
        }
        
        # Detect potential style
        detected_style = "gaming"  # Default to gaming
        for style, keywords in style_keywords.items():
            for keyword in keywords:
                if keyword in basic_prompt.lower():
                    detected_style = style
                    break
        
        # Check if text content is mentioned
        text_match = re.search(r'"([^"]*)"', basic_prompt) or re.search(r"'([^']*)'", basic_prompt)
        text_content = text_match.group(1) if text_match else ""
        
        if not text_content and "text" in basic_prompt.lower():
            # Try to extract text after "text" or "says"
            text_parts = re.split(r'text |says |saying ', basic_prompt.lower())
            if len(text_parts) > 1:
                text_content = text_parts[1].strip().split('.')[0].strip()
        
        # Check for positioning instructions
        position_text = ""
        if "character on right" in basic_prompt.lower() or "character at right" in basic_prompt.lower():
            position_text = "character on right"
        elif "character on left" in basic_prompt.lower() or "character at left" in basic_prompt.lower():
            position_text = "character on left"
        
        # Check for text styling preferences
        text_style = ""
        if "bold" in basic_prompt.lower():
            text_style = "bold"
        if "italic" in basic_prompt.lower():
            text_style = f"{text_style} italic".strip()
            
        # Check text size
        text_size = ""
        if "large text" in basic_prompt.lower() or "big text" in basic_prompt.lower():
            text_size = "large"
        elif "small text" in basic_prompt.lower():
            text_size = "small"
        
        # Check for text alignment
        text_align = ""
        if "center align" in basic_prompt.lower() or "centered text" in basic_prompt.lower():
            text_align = "center-aligned"
        elif "left align" in basic_prompt.lower():
            text_align = "left-aligned"
        elif "right align" in basic_prompt.lower():
            text_align = "right-aligned"
        else:
            text_align = "center-aligned"  # Default
            
        # Generate enhanced prompt
        enhanced = f"Create a {detected_style} thumbnail with "
        
        if position_text:
            enhanced += f"{position_text}, "
            
        if "background" not in basic_prompt.lower() and "remove background" not in basic_prompt.lower():
            enhanced += "background removed, "
        elif "dark background" in basic_prompt.lower():
            enhanced += "dark background, "
        elif "light background" in basic_prompt.lower():
            enhanced += "light background, "
            
        enhanced += "add red arrows pointing to important elements. "
        
        # Build text style string
        style_parts = []
        if text_size:
            style_parts.append(text_size)
        if text_style:
            style_parts.append(text_style)
        text_style_str = " ".join(style_parts)
        
        if text_content:
            # Use the text in all caps for better visibility
            enhanced += f"Place '{text_content.upper()}' text at top in yellow with black outline, {text_align}"
            if text_style_str:
                enhanced += f", using {text_style_str} text. "
            else:
                enhanced += ". "
        else:
            enhanced += f"Add {text_style_str} text at top in yellow with black outline, {text_align}. "
        
        # Add spiral effect if mentioned
        if "spiral" in basic_prompt.lower():
            enhanced += "Add spiral design elements for visual interest. "
            
        # Final styling based on content type
        if detected_style == "gaming" or detected_style == "reaction":
            enhanced += "Add shocked expression effect and a dark gaming style with vibrant accents."
        else:
            enhanced += f"Optimize for high-contrast {detected_style} style with clean visual hierarchy."
        
        return jsonify({
            'success': True,
            'enhanced_prompt': enhanced
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# In app.py, add this function for initialization
def download_google_fonts():
    """Download Google Fonts for thumbnail text if not already present"""
    fonts_path = Config.FONTS_PATH
    os.makedirs(fonts_path, exist_ok=True)
    
    font_urls = {
        "Montserrat-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Bold.ttf",
        "Roboto-Black.ttf": "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Black.ttf",
        "Poppins-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf"
    }
    
    import urllib.request
    
    for font_name, url in font_urls.items():
        font_path = os.path.join(fonts_path, font_name)
        if not os.path.exists(font_path):
            try:
                print(f"Downloading {font_name}...")
                urllib.request.urlretrieve(url, font_path)
                print(f"Downloaded {font_name} successfully")
            except Exception as e:
                print(f"Failed to download {font_name}: {e}")

# Call this function during initialization
download_google_fonts()


if __name__ == '__main__':
    app.run(debug=True)