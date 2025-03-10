from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageFilter, ImageChops
import numpy as np
import os
import json
from src.config.settings import Config
from src.ai.content_analyzer import ContentAnalyzer

class ThumbnailGenerator:
    def __init__(self, model):
        self.model = model
        self.content_analyzer = ContentAnalyzer()
        self.templates = self._load_templates()
        
    def _load_templates(self):
        """Load all template definitions"""
        templates = {}
        template_files = os.listdir(Config.TEMPLATES_PATH)
        
        for template_file in template_files:
            if template_file.endswith('.json'):
                with open(os.path.join(Config.TEMPLATES_PATH, template_file), 'r') as f:
                    template_data = json.load(f)
                    templates[template_data['name']] = template_data
        
        return templates
    
    def generate_thumbnail(self, image, prompt_properties=None):
        """Generate a thumbnail based on image and prompt properties"""
        # Make a copy of the original image
        img = image.copy()
        
        # First apply AI enhancements using the model
        enhanced_image = self.model.predict(img)
        
        # Analyze image content
        content_info = self.content_analyzer.analyze(enhanced_image)
        
        # Select template based on prompt properties
        template_name = "Attractive Thumbnail"  # Default
        if prompt_properties and "style" in prompt_properties:
            # Map style to template name
            style = prompt_properties["style"]
            if style == "gaming":
                template_name = "Attractive Thumbnail"  # Could have gaming-specific template
        
        # Get template or use default
        template = self.templates.get(template_name, next(iter(self.templates.values())))
        
        # Apply the chosen template (with all our fixes)
        thumbnail = self._apply_template(enhanced_image, template, prompt_properties)
        
        return thumbnail
    
    def _apply_template(self, image, template, prompt_properties):
        """Apply a template to an image with layered compositing"""
        img = image.copy()
        width, height = img.size
        
        # ======= REMOVE DUPLICATED BACKGROUND CODE =======
        # We'll use only one background removal implementation
        
        # Background handling - this is the consolidated version
        if prompt_properties and prompt_properties.get("remove_background", False):
            # Extract faces/subjects
            content_info = self.content_analyzer.analyze(img)
            faces = content_info['faces']
            
            if len(faces) > 0:
                # Apply background removal
                foreground_elements = self.content_analyzer.remove_background(img)
                
                # Determine background color or image
                background_color = None
                
                # Check prompt for background preferences
                if "background" in prompt_properties.get("raw_prompt", "").lower():
                    for color in ["black", "dark", "light", "red", "blue", "green", "yellow"]:
                        if color + " background" in prompt_properties.get("raw_prompt", "").lower():
                            if color == "dark":
                                background_color = (20, 20, 20, 255)  # Fully opaque
                            elif color == "light":
                                background_color = (240, 240, 240, 255)  # Fully opaque
                            elif color == "black":
                                background_color = (0, 0, 0, 255)
                            elif color == "red":
                                background_color = (220, 30, 30, 255)
                            elif color == "blue":
                                background_color = (30, 30, 220, 255)
                            elif color == "green":
                                background_color = (30, 180, 30, 255)
                            elif color == "yellow":
                                background_color = (240, 240, 30, 255)
                
                # Create the new background
                if background_color:
                    # Use specified background color
                    background = Image.new('RGBA', img.size, background_color)
                else:
                    # Use dark gradient as default background
                    background = Image.new('RGBA', img.size, (0, 0, 0, 0))
                    draw = ImageDraw.Draw(background)
                    for y in range(height):
                        # Create gradient from dark to darker
                        color = (20, 20, 20, 255 - int(y * 0.1))
                        draw.line([(0, y), (width, y)], fill=color)
                
                # This is the critical line that was causing the problem:
                # Composite the foreground OVER the background (order matters!)
                img = Image.alpha_composite(background, foreground_elements)
        
        # Apply overlay elements
        for element in template['layout']['elements']:
            if element['type'] == 'overlay':
                opacity = element.get('opacity', 0.3)
                color = element.get('color', '#000000')
                
                # Only apply overlay if no custom background was specified
                if not prompt_properties or not "background" in prompt_properties.get("raw_prompt", "").lower():
                    # Convert hex color to RGB
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                    
                    # Create overlay
                    overlay = Image.new('RGBA', img.size, (r, g, b, int(opacity * 255)))
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    img = Image.alpha_composite(img, overlay)
        
        # ======== REST OF THE METHOD REMAINS THE SAME ========
        # Convert back to RGB for drawing operations
        img = img.convert('RGB')
        draw = ImageDraw.Draw(img)
        
        # Process arrows, text, etc...
        # Position arrows based on prompt instructions if available
        if prompt_properties and 'positions' in prompt_properties:
            # Handle pointing arrows from character to enemy
            if 'arrow' in prompt_properties['positions'] and 'character' in prompt_properties['positions']:
                char_pos = prompt_properties['positions']['character']
                arrow_target = None
                
                # Check for enemy mentions in prompt
                if 'enemy' in prompt_properties['raw_prompt'].lower() and 'left' in prompt_properties['raw_prompt'].lower():
                    arrow_target = 'left'
                elif 'enemy' in prompt_properties['raw_prompt'].lower() and 'right' in prompt_properties['raw_prompt'].lower():
                    arrow_target = 'right'
                
                if char_pos == 'right' and arrow_target == 'left':
                    # Draw arrow pointing from right to left
                    arrow_element = {
                        'type': 'arrow',
                        'x': width // 3,  # Arrow head at 1/3 of width (left side)
                        'y': height // 2,
                        'rotation': 180,  # Point left
                        'color': '#FF0000',
                        'size': 100
                    }
                    self._draw_arrow(draw, arrow_element)
                elif char_pos == 'left' and arrow_target == 'right':
                    # Draw arrow pointing from left to right
                    arrow_element = {
                        'type': 'arrow',
                        'x': 2 * width // 3,  # Arrow head at 2/3 of width (right side)
                        'y': height // 2,
                        'rotation': 0,  # Point right
                        'color': '#FF0000',
                        'size': 100
                    }
                    self._draw_arrow(draw, arrow_element)
            elif 'arrow' in prompt_properties['positions']:
                arrow_position = prompt_properties['positions']['arrow']
                
                # Calculate arrow positions based on requested position
                arrow_positions = []
                if arrow_position == 'top':
                    arrow_positions.append({'x': width // 2, 'y': height // 6, 'rotation': 90})
                elif arrow_position == 'bottom':
                    arrow_positions.append({'x': width // 2, 'y': 5 * height // 6, 'rotation': -90})
                elif arrow_position == 'left':
                    arrow_positions.append({'x': width // 6, 'y': height // 2, 'rotation': 0})
                elif arrow_position == 'right':
                    arrow_positions.append({'x': 5 * width // 6, 'y': height // 2, 'rotation': 180})
                elif arrow_position == 'corner':
                    arrow_positions.append({'x': width // 6, 'y': height // 6, 'rotation': 45})
                    arrow_positions.append({'x': 5 * width // 6, 'y': 5 * height // 6, 'rotation': -135})
                
                # Draw arrows at calculated positions
                for pos in arrow_positions:
                    element = {
                        'type': 'arrow',
                        'x': pos['x'],
                        'y': pos['y'],
                        'rotation': pos['rotation'],
                        'color': '#FF0000',
                        'size': 80
                    }
                    self._draw_arrow(draw, element)
        
        # Add other template elements (if not overridden by prompt)
        else:
            for element in template['layout']['elements']:
                if element['type'] == 'arrow':
                    self._draw_arrow(draw, element)
                elif element['type'] == 'shape' and element['shape'] != 'overlay':
                    self._draw_shape(draw, element)
        
        # Add text with proper alignment if specified in prompt
        if prompt_properties and 'text_overlay' in prompt_properties and prompt_properties['text_overlay']:
            # Get text areas from template
            text_areas = template['layout']['textAreas']
            
            # Modify text area based on positioning instructions
            if 'positions' in prompt_properties and 'text' in prompt_properties['positions']:
                text_position = prompt_properties['positions']['text']
                
                # Set text area position
                if text_position == 'top':
                    text_areas[0]['y'] = height // 6
                elif text_position == 'bottom':
                    text_areas[0]['y'] = 5 * height // 6
                elif text_position == 'left':
                    text_areas[0]['x'] = width // 4
                elif text_position == 'right':
                    text_areas[0]['x'] = 3 * width // 4
                elif text_position == 'center':
                    text_areas[0]['x'] = width // 2
                    text_areas[0]['y'] = height // 2
            
            # Add alignment information
            text_areas[0]['align'] = prompt_properties.get('text_alignment', 'center')
            
            # Draw the text
            self._add_text(draw, prompt_properties['text_overlay'], text_areas)
        
        return img
    
    def _add_spiral_effect(self, image):
        """Add spiral design elements to the background"""
        width, height = image.size
        draw = ImageDraw.Draw(image, 'RGBA')
        
        # Create spirals in corners
        spiral_points = []
        center_x, center_y = width // 5, height // 5
        
        # Generate spiral points
        for i in range(0, 720, 15):
            angle = i * 0.1
            radius = i * 0.05
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            spiral_points.append((x, y))
        
        # Draw spiral with gradient color
        for i in range(1, len(spiral_points)):
            alpha = 150 - i // 2
            if alpha < 30:
                alpha = 30
            draw.line([spiral_points[i-1], spiral_points[i]], 
                     fill=(255, 255, 0, alpha), width=5)
        
        # Add another spiral in bottom right
        spiral_points = []
        center_x, center_y = width * 4 // 5, height * 4 // 5
        
        for i in range(0, 720, 15):
            angle = i * 0.1
            radius = i * 0.05
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            spiral_points.append((x, y))
        
        for i in range(1, len(spiral_points)):
            alpha = 150 - i // 2
            if alpha < 30:
                alpha = 30
            draw.line([spiral_points[i-1], spiral_points[i]], 
                     fill=(255, 0, 0, alpha), width=5)
    
    def _draw_arrow(self, draw, element):
        """Draw a customizable arrow on the image"""
        # Get arrow properties with more customization options
        x, y = element['x'], element['y']
        
        # Color with fallback and support for hex values
        color = element.get('color', '#FF0000')
        if isinstance(color, str) and color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            color = (r, g, b)
        
        rotation = element.get('rotation', 0)
        size = element.get('size', 100)  # Make arrows bigger by default
        thickness = element.get('thickness', 1.5)  # Thicker arrows
        
        # Scale points based on thickness
        wing_width = int(size//3 * thickness)
        
        # Define arrow points for larger, more visible arrow
        points = [
            (x, y - size//2),  # Top point
            (x - wing_width, y + size//2),  # Bottom left
            (x - wing_width//2, y + size//4),  # Bottom middle left indent
            (x - wing_width//2, y + size//2),  # Bottom left corner
            (x + wing_width//2, y + size//2),  # Bottom right corner
            (x + wing_width//2, y + size//4),  # Bottom middle right indent
            (x + wing_width, y + size//2),  # Bottom right
        ]
        
        # Rotate points for arrow direction
        if rotation:
            # Convert rotation to radians
            angle_rad = rotation * (3.14159 / 180)
            cos_angle = np.cos(angle_rad)
            sin_angle = np.sin(angle_rad)
            
            # Rotate around (x, y)
            rotated_points = []
            for px, py in points:
                tx, ty = px - x, py - y
                rx = tx * cos_angle - ty * sin_angle
                ry = tx * sin_angle + ty * cos_angle
                rotated_points.append((rx + x, ry + y))
            points = rotated_points
        
        # Draw the arrow with a visible outline - with stronger colors
        if isinstance(color, tuple):
            # RGB color
            fill_color = color
            outline_color = (0, 0, 0)
        else:
            # String color like '#FF0000'
            fill_color = color
            outline_color = "#000000"
        
        # Draw fill
        draw.polygon(points, fill=fill_color)
        
        # Draw thick outline for better visibility
        draw.line([points[-1], points[0]] + points, fill=outline_color, width=3)
    
    def _draw_shape(self, draw, element):
        """Draw a shape on the image"""
        if element['shape'] == 'rectangle':
            draw.rectangle(
                [element['x'], element['y'], element['x'] + element['width'], element['y'] + element['height']],
                fill=element['color']
            )
        # Other shapes...
    
    def _add_text(self, draw, text, text_areas):
        """Add text to the image with enhanced styling"""
        if not text_areas or not text:
            return
        
        # Get text styling info
        text_area = text_areas[0]
        font_size = text_area.get('fontSize', 60)
        text_align = text_area.get('align', 'center')
        is_bold = 'bold' in text_area.get('style', '').lower()
        is_italic = 'italic' in text_area.get('style', '').lower()
        
        # Try to use Google Fonts if available
        font = None
        try:
            # Modern eye-catching YouTube fonts
            youtube_fonts = [
                'Montserrat-Bold.ttf',
                'Roboto-Black.ttf',
                'OpenSans-ExtraBold.ttf',
                'Poppins-Bold.ttf',
                os.path.join(Config.FONTS_PATH, 'Montserrat-Bold.ttf'),
                os.path.join(Config.FONTS_PATH, 'Roboto-Black.ttf'),
                'C:\\Windows\\Fonts\\Arial.ttf'
            ]
            
            # Try each font until one works
            for font_path in youtube_fonts:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except Exception:
                    continue
        except Exception:
            pass
            
        # Fallback to default if no Google Font was loaded
        if font is None:
            font = ImageFont.load_default()
        
        # Calculate text position
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(text, font=font)
        
        # Get position and apply alignment
        x = text_area['x']
        y = text_area['y']
        
        # Calculate position based on alignment and placement
        if text_align == 'center':
            x -= (text_width // 2)
        elif text_align == 'right':
            x -= text_width
        
        # Get text colors
        stroke_width = text_area.get('strokeWidth', 4)
        stroke_color = text_area.get('strokeColor', '#000000')
        text_color = text_area.get('color', '#FFFFFF')
        
        # Convert hex colors to RGB
        if isinstance(stroke_color, str) and stroke_color.startswith('#'):
            r = int(stroke_color[1:3], 16)
            g = int(stroke_color[3:5], 16)
            b = int(stroke_color[5:7], 16)
            stroke_color = (r, g, b)
        
        if isinstance(text_color, str) and text_color.startswith('#'):
            r = int(text_color[1:3], 16)
            g = int(text_color[3:5], 16)
            b = int(text_color[5:7], 16)
            text_color = (r, g, b)
            
        # Draw outline for better visibility - using more points for better coverage
        for offset_x in range(-stroke_width, stroke_width+1, 1):
            for offset_y in range(-stroke_width, stroke_width+1, 1):
                if offset_x == 0 and offset_y == 0:
                    continue
                if abs(offset_x) + abs(offset_y) <= stroke_width + 1:
                    draw.text((x + offset_x, y + offset_y), text, font=font, fill=stroke_color)
        
        # Draw main text with a slight shadow for depth
        draw.text((x, y), text, font=font, fill=text_color)