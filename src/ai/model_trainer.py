import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Input, Dense, Conv2D, MaxPooling2D, Flatten, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from PIL import Image
import time
from src.utils.database import ThumbnailDatabase
from src.config.settings import Config

class ModelTrainer:
    def __init__(self):
        self.db = ThumbnailDatabase()
        self.batch_size = 16
        self.img_height = 720
        self.img_width = 1280
        
    def prepare_dataset(self, min_rating=4):
        """Prepare a dataset from highly-rated thumbnails"""
        print("Preparing dataset from user feedback...")
        
        # Get highly rated thumbnails from DB
        highly_rated = self.db.get_highly_rated_thumbnails(min_rating=min_rating)
        
        if len(highly_rated) < 10:
            print(f"Not enough data for training, only {len(highly_rated)} samples available")
            return None, None
            
        print(f"Found {len(highly_rated)} highly-rated thumbnails for training")
        
        # Prepare data arrays
        input_images = []
        output_images = []
        
        for item in highly_rated:
            # Get original and thumbnail paths
            thumb_path = item['thumbnail_path']
            if thumb_path.startswith('/'):
                thumb_path = thumb_path[1:]  # Remove leading slash
                
            # Get the original path
            # The database stores the web path, convert to filesystem path
            original_path = thumb_path.replace('thumbnails', 'uploads')
            original_path = original_path.replace('ai_thumbnail_', '')
                
            # Load images if they exist
            full_thumb_path = os.path.join(Config.OUTPUT_PATH, os.path.basename(thumb_path))
            full_orig_path = os.path.join('uploads', os.path.basename(original_path))
            
            if os.path.exists(full_thumb_path) and os.path.exists(full_orig_path):
                # Load and preprocess images
                try:
                    # Input is the original image
                    input_img = load_img(full_orig_path, target_size=(self.img_height, self.img_width))
                    input_array = img_to_array(input_img) / 255.0
                    input_images.append(input_array)
                    
                    # Output is the enhanced thumbnail
                    output_img = load_img(full_thumb_path, target_size=(self.img_height, self.img_width))
                    output_array = img_to_array(output_img) / 255.0
                    output_images.append(output_array)
                except Exception as e:
                    print(f"Error loading images: {e}")
        
        if len(input_images) < 10:
            print(f"Not enough valid images for training, only {len(input_images)} samples available")
            return None, None
            
        # Convert to numpy arrays
        X = np.array(input_images)
        y = np.array(output_images)
        
        return X, y
    
    def build_enhancement_model(self):
        """Build a CNN model for image enhancement"""
        # Input layer
        input_img = Input(shape=(self.img_height, self.img_width, 3))
        
        # Encoder (downsampling)
        x = Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
        x = MaxPooling2D((2, 2), padding='same')(x)
        x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
        encoded = MaxPooling2D((2, 2), padding='same')(x)
        
        # Decoder (upsampling)
        x = Conv2D(64, (3, 3), activation='relu', padding='same')(encoded)
        x = tf.keras.layers.UpSampling2D((2, 2))(x)
        x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
        x = tf.keras.layers.UpSampling2D((2, 2))(x)
        
        # Output layer
        decoded = Conv2D(3, (3, 3), activation='sigmoid', padding='same')(x)
        
        # Create model
        model = Model(input_img, decoded)
        model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])
        
        return model
    
    def train_model(self, epochs=10):
        """Train the model using collected data"""
        # Prepare dataset
        X, y = self.prepare_dataset()
        if X is None or len(X) == 0:
            print("Not enough data to train model")
            return False
        
        # Split into training and validation sets
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Build model
        model = self.build_enhancement_model()
        print("Starting model training...")
        
        # Train the model
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=self.batch_size,
            validation_data=(X_val, y_val)
        )
        
        # Save the model
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        model_path = os.path.join(Config.MODEL_PATH, f'enhancement_model_{timestamp}')
        model.save(model_path)
        
        # Update the current model path
        latest_model_path = os.path.join(Config.MODEL_PATH, 'latest')
        if os.path.exists(latest_model_path):
            os.unlink(latest_model_path)
        os.symlink(model_path, latest_model_path)
        
        print(f"Model trained and saved to {model_path}")
        return True