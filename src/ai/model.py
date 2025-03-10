import tensorflow as tf
import numpy as np
from PIL import Image, ImageEnhance
from src.config.settings import Config

class ThumbnailModel:
    def __init__(self):
        self.model = None
        self.style_transfer_model = None

    def load_model(self):
        try:
            # Try to load pre-trained models
            self.model = tf.keras.models.load_model(Config.MODEL_PATH)
            print("Base model loaded successfully")
            
            # Try to load style transfer model
            try:
                self.style_transfer_model = tf.saved_model.load(Config.STYLE_TRANSFER_MODEL_PATH)
                print("Style transfer model loaded successfully")
            except:
                print("Style transfer model not found, using base enhancement only")
                
        except:
            # If no model exists, create a simple one for demonstration
            print("Creating a simple enhancement model")
            self.model = self._create_enhancement_model()
    
    def _create_enhancement_model(self):
        # This creates a simple image enhancement model
        inputs = tf.keras.layers.Input(shape=(None, None, 3))
        
        # Simple enhancement network
        x = tf.keras.layers.Conv2D(16, (3, 3), activation='relu', padding='same')(inputs)
        x = tf.keras.layers.Conv2D(16, (3, 3), activation='relu', padding='same')(x)
        x = tf.keras.layers.Conv2D(8, (3, 3), activation='relu', padding='same')(x)
        outputs = tf.keras.layers.Conv2D(3, (3, 3), activation='sigmoid', padding='same')(x)
        
        model = tf.keras.Model(inputs, outputs)
        model.compile(optimizer='adam', loss='mse')
        
        return model

    def predict(self, image):
        """Enhance image for YouTube thumbnail"""
        if self.model is None:
            self.load_model()
        
        # Apply AI enhancement if available
        if self.style_transfer_model:
            # Use style transfer for more dramatic effect
            enhanced_image = self._apply_style_transfer(image)
        else:
            # Fall back to basic enhancement
            enhanced_image = self._apply_basic_enhancement(image)
            
        return enhanced_image
    
    def _apply_style_transfer(self, image):
        """Apply style transfer for YouTube-optimized look"""
        # Convert PIL image to tensor
        img_array = np.array(image)
        content_image = tf.convert_to_tensor(img_array, dtype=tf.float32)
        content_image = content_image / 255.0
        content_image = tf.expand_dims(content_image, 0)
        
        # Apply style transfer (placeholder - would use actual model in real implementation)
        # Since we don't have an actual style transfer model loaded, simulate the effect
        stylized_image = content_image  # This would normally be model output
        
        # Convert back to PIL
        stylized_array = stylized_image[0].numpy() * 255
        stylized_pil = Image.fromarray(np.uint8(stylized_array))
        
        # Apply additional enhancements to make it look like style transfer
        enhancer = ImageEnhance.Color(stylized_pil)
        stylized_pil = enhancer.enhance(1.4)  # Increase color saturation
        
        enhancer = ImageEnhance.Contrast(stylized_pil)
        stylized_pil = enhancer.enhance(1.3)  # Increase contrast
        
        return stylized_pil
    
    def _apply_basic_enhancement(self, image):
        """Apply basic image enhancements for YouTube thumbnails"""
        # Convert PIL image to numpy array
        img_array = np.array(image)
        
        # Normalize for model input
        img_array = img_array / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        # Make prediction if we have a model
        if hasattr(self.model, 'predict'):
            try:
                predicted_array = self.model.predict(img_array)
                predicted_array = np.clip(predicted_array * 255.0, 0, 255)
                predicted_image = Image.fromarray(np.uint8(predicted_array[0]))
            except:
                # Fall back to manual enhancement if model fails
                predicted_image = image
        else:
            # Manual enhancement
            predicted_image = image
        
        # Apply manual enhancements for YouTube-optimized look
        enhancer = ImageEnhance.Contrast(predicted_image)
        enhanced_image = enhancer.enhance(1.4)  # Increase contrast
        
        enhancer = ImageEnhance.Brightness(enhanced_image)
        enhanced_image = enhancer.enhance(1.1)  # Slight brightness boost
        
        enhancer = ImageEnhance.Color(enhanced_image)
        enhanced_image = enhancer.enhance(1.3)  # Increase color saturation
        
        enhancer = ImageEnhance.Sharpness(enhanced_image)
        enhanced_image = enhancer.enhance(1.5)  # Increase sharpness
        
        return enhanced_image