"""
Image Utilities Service
Handles image preprocessing, enhancement, and format conversion
"""

import cv2
import numpy as np
from PIL import Image
import logging
from typing import Tuple, Optional
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageUtils:
    """Utility class for image processing and enhancement"""
    
    # Supported image formats
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.pdf']
    
    @staticmethod
    def load_image(image_path: str) -> Optional[np.ndarray]:
        """
        Load image from file path
        
        Args:
            image_path: Path to image file
            
        Returns:
            Image as numpy array or None if failed
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Failed to read image: {image_path}")
                return None
            
            logger.info(f"Image loaded successfully: {image_path}")
            return img
        
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            return None
    
    @staticmethod
    def get_image_info(image_path: str) -> dict:
        """
        Get detailed information about an image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with image information
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {"error": "Failed to read image"}
            
            height, width = img.shape[:2]
            file_size = os.path.getsize(image_path) / (1024 * 1024)  # Size in MB
            
            return {
                "width": width,
                "height": height,
                "dimensions": f"{width}x{height}",
                "file_size_mb": round(file_size, 2),
                "file_size_bytes": os.path.getsize(image_path),
                "format": os.path.splitext(image_path)[1].lower()
            }
        
        except Exception as e:
            logger.error(f"Error getting image info: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def resize_image(image: np.ndarray, max_width: int = 3000, max_height: int = 3000) -> np.ndarray:
        """
        Resize image if it exceeds maximum dimensions
        
        Args:
            image: Input image
            max_width: Maximum width
            max_height: Maximum height
            
        Returns:
            Resized image
        """
        try:
            height, width = image.shape[:2]
            
            if width <= max_width and height <= max_height:
                return image
            
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            logger.info(f"Image resized from {width}x{height} to {new_width}x{new_height}")
            
            return resized
        
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            return image
    
    @staticmethod
    def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale
        
        Args:
            image: Input image
            
        Returns:
            Grayscale image
        """
        try:
            if len(image.shape) == 2:
                return image  # Already grayscale
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            logger.info("Image converted to grayscale")
            return gray
        
        except Exception as e:
            logger.error(f"Error converting to grayscale: {str(e)}")
            return image
    
    @staticmethod
    def denoise_image(image: np.ndarray, strength: int = 10) -> np.ndarray:
        """
        Remove noise from image
        
        Args:
            image: Input image
            strength: Denoising strength (1-30)
            
        Returns:
            Denoised image
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply bilateral filter (better for document images)
            denoised = cv2.bilateralFilter(gray, 9, strength, strength)
            logger.info(f"Image denoised with strength: {strength}")
            
            return denoised
        
        except Exception as e:
            logger.error(f"Error denoising image: {str(e)}")
            return image
    
    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        """
        Enhance image contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        
        Args:
            image: Input image
            
        Returns:
            Contrast-enhanced image
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            logger.info("Image contrast enhanced using CLAHE")
            
            return enhanced
        
        except Exception as e:
            logger.error(f"Error enhancing contrast: {str(e)}")
            return image
    
    @staticmethod
    def apply_threshold(image: np.ndarray, threshold_value: int = 127) -> np.ndarray:
        """
        Apply binary threshold to image
        
        Args:
            image: Input image
            threshold_value: Threshold value (0-255)
            
        Returns:
            Binary image
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply Otsu's thresholding (automatic)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            logger.info("Binary threshold applied")
            
            return binary
        
        except Exception as e:
            logger.error(f"Error applying threshold: {str(e)}")
            return image
    
    @staticmethod
    def deskew_image(image: np.ndarray) -> np.ndarray:
        """
        Deskew image (correct rotation)
        
        Args:
            image: Input image
            
        Returns:
            Deskewed image
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Get contours
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) == 0:
                logger.warning("No contours found for deskewing")
                return image
            
            # Get largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Get rotation angle
            rect = cv2.minAreaRect(largest_contour)
            angle = rect[2]
            
            # Rotate image
            if angle != 0:
                h, w = image.shape[:2]
                M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
                rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                logger.info(f"Image deskewed by {angle} degrees")
                return rotated
            
            return image
        
        except Exception as e:
            logger.error(f"Error deskewing image: {str(e)}")
            return image
    
    @staticmethod
    def preprocess_for_ocr(image_path: str) -> np.ndarray:
        """
        Complete preprocessing pipeline for OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image
        """
        try:
            logger.info("Starting OCR preprocessing pipeline")
            
            # Load image
            img = ImageUtils.load_image(image_path)
            if img is None:
                return None
            
            # Resize if too large
            img = ImageUtils.resize_image(img)
            
            # Deskew
            img = ImageUtils.deskew_image(img)
            
            # Convert to grayscale
            img = ImageUtils.convert_to_grayscale(img)
            
            # Denoise
            img = ImageUtils.denoise_image(img, strength=15)
            
            # Enhance contrast
            img = ImageUtils.enhance_contrast(img)
            
            logger.info("OCR preprocessing completed")
            return img
        
        except Exception as e:
            logger.error(f"Error in preprocessing pipeline: {str(e)}")
            return None
    
    @staticmethod
    def preprocess_for_tampering_detection(image_path: str) -> np.ndarray:
        """
        Preprocessing pipeline for tampering detection
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image
        """
        try:
            logger.info("Starting tampering detection preprocessing")
            
            img = ImageUtils.load_image(image_path)
            if img is None:
                return None
            
            # Resize if too large
            img = ImageUtils.resize_image(img, max_width=2000, max_height=2000)
            
            # Light denoising to preserve details
            img = ImageUtils.denoise_image(img, strength=5)
            
            logger.info("Tampering detection preprocessing completed")
            return img
        
        except Exception as e:
            logger.error(f"Error in tampering detection preprocessing: {str(e)}")
            return None
    
    @staticmethod
    def get_image_statistics(image: np.ndarray) -> dict:
        """
        Calculate image statistics
        
        Args:
            image: Input image
            
        Returns:
            Dictionary with statistics
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Calculate statistics
            mean = np.mean(gray)
            std_dev = np.std(gray)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Histogram
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            
            return {
                "mean": float(mean),
                "std_dev": float(std_dev),
                "laplacian_variance": float(laplacian_var),
                "min_value": float(np.min(gray)),
                "max_value": float(np.max(gray)),
                "histogram_bins": 256
            }
        
        except Exception as e:
            logger.error(f"Error calculating image statistics: {str(e)}")
            return {}
    
    @staticmethod
    def save_image(image: np.ndarray, output_path: str) -> bool:
        """
        Save image to file
        
        Args:
            image: Image to save
            output_path: Path where to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = cv2.imwrite(output_path, image)
            if success:
                logger.info(f"Image saved: {output_path}")
                return True
            else:
                logger.error(f"Failed to save image: {output_path}")
                return False
        
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            return False
    
    @staticmethod
    def crop_image(image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
        """
        Crop image region
        
        Args:
            image: Input image
            x: X coordinate
            y: Y coordinate
            width: Width of crop
            height: Height of crop
            
        Returns:
            Cropped image
        """
        try:
            cropped = image[y:y+height, x:x+width]
            logger.info(f"Image cropped to {width}x{height}")
            return cropped
        
        except Exception as e:
            logger.error(f"Error cropping image: {str(e)}")
            return image
    
    @staticmethod
    def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
        """
        Rotate image by specified angle
        
        Args:
            image: Input image
            angle: Rotation angle in degrees
            
        Returns:
            Rotated image
        """
        try:
            h, w = image.shape[:2]
            M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h))
            logger.info(f"Image rotated by {angle} degrees")
            return rotated
        
        except Exception as e:
            logger.error(f"Error rotating image: {str(e)}")
            return image