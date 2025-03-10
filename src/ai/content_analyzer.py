import cv2
import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image as keras_image

class ContentAnalyzer:
    def __init__(self):
        self.model = ResNet50(weights='imagenet', include_top=False)
        # Load face detection model
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def analyze(self, image):
        """Analyze image content and return content info"""
        # Convert PIL image to numpy array for OpenCV
        img_array = np.array(image)
        img_cv = img_array[:, :, ::-1].copy()  # Convert RGB to BGR for OpenCV
        
        # Analyze image for face detection
        faces = self.detect_faces(img_cv)
        
        # Get image features using ResNet
        features = self.extract_features(image)
        
        # Analyze image brightness/contrast
        brightness, contrast = self.analyze_lighting(img_array)
        
        # Find optimal text placement areas (areas with less detail)
        text_regions = self.find_text_regions(img_array)
        
        return {
            'faces': faces,
            'features': features,
            'brightness': brightness,
            'contrast': contrast,
            'text_regions': text_regions
        }
    
    def detect_faces(self, img_cv):
        """Detect faces in the image"""
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        return faces
    
    def extract_features(self, img):
        """Extract image features using ResNet"""
        # Resize for ResNet
        img_resized = img.resize((224, 224))
        x = keras_image.img_to_array(img_resized)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        
        # Get features
        features = self.model.predict(x)
        return features
    
    def analyze_lighting(self, img_array):
        """Analyze image brightness and contrast"""
        # Convert to grayscale
        if len(img_array.shape) == 3:
            img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            img_gray = img_array
            
        # Calculate brightness
        brightness = np.mean(img_gray)
        
        # Calculate contrast
        contrast = np.std(img_gray)
        
        return brightness, contrast
    
    def find_text_regions(self, img_array):
        """Find regions suitable for text placement"""
        # Convert to grayscale
        if len(img_array.shape) == 3:
            img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            img_gray = img_array
            
        # Apply edge detection
        edges = cv2.Canny(img_gray, 100, 200)
        
        # Find regions with low edge density (good for text)
        kernel = np.ones((20, 20), np.uint8)
        edge_density = cv2.filter2D(edges, -1, kernel)
        
        # Get top regions with lowest edge density
        h, w = edge_density.shape
        regions = []
        
        # Top region
        top_score = np.sum(edge_density[:h//3, :])
        regions.append(('top', top_score))
        
        # Bottom region
        bottom_score = np.sum(edge_density[2*h//3:, :])
        regions.append(('bottom', bottom_score))
        
        # Middle region
        middle_score = np.sum(edge_density[h//3:2*h//3, :])
        regions.append(('middle', middle_score))
        
        # Sort by lowest edge density (best for text)
        regions.sort(key=lambda x: x[1])
        
        return [r[0] for r in regions]
    
    def remove_background(self, image, target_area=None):
        """Remove background from a person in the image"""
        # Convert PIL image to numpy array for OpenCV
        img_array = np.array(image)
        img_cv = img_array[:, :, ::-1].copy()  # Convert RGB to BGR for OpenCV
        
        # If target area provided, crop to that area
        if target_area:
            x, y, w, h = target_area
            img_cv = img_cv[y:y+h, x:x+w]
        
        # Create a mask using GrabCut algorithm
        mask = np.zeros(img_cv.shape[:2], np.uint8)
        
        # Set up the rectangle for GrabCut
        rect = None
        if target_area:
            rect = (0, 0, img_cv.shape[1], img_cv.shape[0])
        else:
            # If no target area, use face detection to help
            faces = self.detect_faces(img_cv)
            if len(faces) > 0:
                # Use the largest face as a guide
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                x, y, w, h = largest_face
                
                # Create a larger rectangle around the face for the body
                face_center_x = x + w//2
                face_center_y = y + h//2
                rect_width = min(img_cv.shape[1], int(w * 3))
                rect_height = min(img_cv.shape[0], int(h * 4))
                rect_x = max(0, face_center_x - rect_width//2)
                rect_y = max(0, face_center_y - rect_height//3)  # Less space above head
                
                rect = (rect_x, rect_y, rect_width, rect_height)
            else:
                # No faces detected, use center of image
                rect = (img_cv.shape[1]//4, img_cv.shape[0]//4, 
                        img_cv.shape[1]//2, img_cv.shape[0]//2)
        
        # Initialize background and foreground models
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        # Apply GrabCut
        if rect:
            try:
                cv2.grabCut(img_cv, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
                
                # Create mask where sure and probable foreground are set to 1
                mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
                
                # Apply the mask to the image
                result = img_cv * mask2[:, :, np.newaxis]
                
                # Convert back to RGB for PIL
                result_rgb = result[:, :, ::-1]
                
                # Create PIL image with alpha channel
                result_img = Image.fromarray(result_rgb).convert("RGBA")
                
                # Create alpha mask from the grayscale mask
                alpha_mask = Image.fromarray((mask2 * 255).astype(np.uint8))
                
                # Apply alpha mask to image
                result_img.putalpha(alpha_mask)
                
                return result_img
                
            except Exception as e:
                print(f"Background removal failed: {e}")
                return image.convert("RGBA")
        
        return image.convert("RGBA")