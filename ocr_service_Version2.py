"""
OCR Service
Dedicated service for text extraction from documents
"""

import logging
from typing import Dict, Optional
import paddleocr
import easyocr
import numpy as np
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCRServiceAdvanced:
    """Advanced OCR service with multiple fallback methods"""
    
    def __init__(self):
        """Initialize OCR services"""
        self.paddle_ocr = None
        self.easy_ocr = None
        self.tesseract_available = False
        
        self._init_paddle_ocr()
        self._init_easy_ocr()
        self._check_tesseract()
        
        logger.info("OCRServiceAdvanced initialized")
    
    def _init_paddle_ocr(self):
        """Initialize PaddleOCR"""
        try:
            self.paddle_ocr = paddleocr.OCR(use_angle_cls=True, lang='en')
            logger.info("PaddleOCR initialized successfully")
        except Exception as e:
            logger.warning(f"PaddleOCR initialization failed: {e}")
            self.paddle_ocr = None
    
    def _init_easy_ocr(self):
        """Initialize EasyOCR"""
        try:
            self.easy_ocr = easyocr.Reader(['en'], gpu=False)
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.warning(f"EasyOCR initialization failed: {e}")
            self.easy_ocr = None
    
    def _check_tesseract(self):
        """Check if Tesseract is available"""
        try:
            import pytesseract
            self.tesseract_available = True
            logger.info("Tesseract OCR available")
        except:
            logger.warning("Tesseract OCR not available")
            self.tesseract_available = False
    
    def extract_with_paddle(self, image_path: str) -> Dict:
        """Extract text using PaddleOCR"""
        try:
            if not self.paddle_ocr:
                return {"text": "", "confidence": 0, "error": "PaddleOCR not available"}
            
            result = self.paddle_ocr.ocr(image_path, cls=True)
            
            extracted_text = ""
            confidence_scores = []
            
            for line in result:
                if line:
                    for word_info in line:
                        text, confidence = word_info[1], word_info[2]
                        extracted_text += text + " "
                        confidence_scores.append(confidence)
            
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
            
            logger.info(f"PaddleOCR extraction completed with confidence: {avg_confidence}")
            
            return {
                "text": extracted_text.strip(),
                "confidence": float(avg_confidence),
                "method": "paddleocr",
                "character_count": len(extracted_text)
            }
        
        except Exception as e:
            logger.error(f"PaddleOCR error: {str(e)}")
            return {"text": "", "confidence": 0, "error": str(e), "method": "paddleocr"}
    
    def extract_with_easy_ocr(self, image_path: str) -> Dict:
        """Extract text using EasyOCR"""
        try:
            if not self.easy_ocr:
                return {"text": "", "confidence": 0, "error": "EasyOCR not available"}
            
            result = self.easy_ocr.readtext(image_path)
            
            extracted_text = ""
            confidence_scores = []
            
            for detection in result:
                text, confidence = detection[1], detection[2]
                extracted_text += text + " "
                confidence_scores.append(confidence)
            
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
            
            logger.info(f"EasyOCR extraction completed with confidence: {avg_confidence}")
            
            return {
                "text": extracted_text.strip(),
                "confidence": float(avg_confidence),
                "method": "easyocr",
                "character_count": len(extracted_text)
            }
        
        except Exception as e:
            logger.error(f"EasyOCR error: {str(e)}")
            return {"text": "", "confidence": 0, "error": str(e), "method": "easyocr"}
    
    def extract_with_tesseract(self, image_path: str) -> Dict:
        """Extract text using Tesseract OCR"""
        try:
            if not self.tesseract_available:
                return {"text": "", "confidence": 0, "error": "Tesseract not available"}
            
            import pytesseract
            from PIL import Image
            
            text = pytesseract.image_to_string(Image.open(image_path))
            
            logger.info("Tesseract extraction completed")
            
            return {
                "text": text.strip(),
                "confidence": 0,  # Tesseract doesn't provide confidence
                "method": "tesseract",
                "character_count": len(text)
            }
        
        except Exception as e:
            logger.error(f"Tesseract error: {str(e)}")
            return {"text": "", "confidence": 0, "error": str(e), "method": "tesseract"}
    
    def extract_best(self, image_path: str) -> Dict:
        """Extract using best available method"""
        results = [
            self.extract_with_paddle(image_path),
            self.extract_with_easy_ocr(image_path),
            self.extract_with_tesseract(image_path)
        ]
        
        # Filter out empty results
        valid_results = [r for r in results if r.get("text") and r.get("confidence", 0) > 0]
        
        if not valid_results:
            # If no confidence scores, pick the one with most text
            valid_results = [r for r in results if r.get("text")]
            if not valid_results:
                return {"text": "", "confidence": 0, "method": "none", "error": "No OCR available"}
            
            return max(valid_results, key=lambda x: len(x.get("text", "")))
        
        best_result = max(valid_results, key=lambda x: x.get("confidence", 0))
        logger.info(f"Best OCR method: {best_result['method']}")
        return best_result
    
    def extract_and_clean(self, image_path: str) -> Dict:
        """Extract text and clean it"""
        result = self.extract_best(image_path)
        
        if result.get("text"):
            # Clean the text
            result["text"] = self._clean_ocr_text(result["text"])
        
        return result
    
    def _clean_ocr_text(self, text: str) -> str:
        """Clean OCR extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common OCR errors
        text = text.replace('|', 'I')  # Pipe to I
        text = text.replace('0', 'O')  # Zero to O (context-dependent)
        
        return text.strip()