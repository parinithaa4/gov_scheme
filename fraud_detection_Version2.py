"""
Fraud Detection Service
Dedicated service for fraud detection and document verification
"""

import logging
from typing import Dict, List, Optional
import hashlib
import imagehash
from PIL import Image
import cv2
import numpy as np
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FraudDetectionServiceAdvanced:
    """Advanced fraud detection service"""
    
    def __init__(self):
        """Initialize fraud detection service"""
        self.suspicious_flags = []
        logger.info("FraudDetectionServiceAdvanced initialized")
    
    # ========== HASHING & DUPLICATE DETECTION ==========
    
    def calculate_hashes(self, image_path: str) -> Dict[str, str]:
        """Calculate multiple hashes for image"""
        try:
            img = Image.open(image_path)
            
            hashes = {
                "md5": self._calculate_md5(image_path),
                "phash": str(imagehash.phash(img)),
                "dhash": str(imagehash.dhash(img)),
                "ahash": str(imagehash.ahash(img)),
                "whash": str(imagehash.whash(img))
            }
            
            logger.info("Image hashes calculated")
            return hashes
        
        except Exception as e:
            logger.error(f"Error calculating hashes: {str(e)}")
            return {}
    
    def _calculate_md5(self, image_path: str) -> str:
        """Calculate MD5 hash"""
        hash_md5 = hashlib.md5()
        with open(image_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def detect_duplicates(self, image_path: str, stored_hashes: List[Dict]) -> Dict:
        """Detect duplicate submissions"""
        current_hashes = self.calculate_hashes(image_path)
        duplicates = []
        
        for stored in stored_hashes:
            # MD5 exact match
            if current_hashes.get("md5") == stored.get("md5"):
                duplicates.append({"type": "exact", "similarity": 1.0})
                continue
            
            # Perceptual hash similarity
            try:
                current_phash = imagehash.ImageHash(int(current_hashes.get("phash", "0"), 16))
                stored_phash = imagehash.ImageHash(int(stored.get("phash", "0"), 16))
                
                similarity = 1 - (current_phash - stored_phash) / len(current_phash.hash.flatten())
                
                if similarity > 0.85:
                    duplicates.append({"type": "perceptual", "similarity": float(similarity)})
            
            except Exception as e:
                logger.warning(f"Error comparing perceptual hashes: {e}")
        
        return {
            "is_duplicate": len(duplicates) > 0,
            "duplicates": duplicates,
            "confidence": min(100, len(duplicates) * 50)
        }
    
    # ========== TAMPERING DETECTION ==========
    
    def detect_tampering(self, image_path: str) -> Dict:
        """Detect image tampering signs"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {"error": "Could not read image"}
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Laplacian variance (sharp vs blurry)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Sobel for edge detection
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
            edge_mag = np.sqrt(sobelx**2 + sobely**2)
            edge_variance = edge_mag.var()
            
            # Color analysis
            img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            saturation = img_hsv[:, :, 1]
            sat_var = saturation.var()
            
            # Noise estimation
            noise_sigma = self._estimate_noise(gray)
            
            tampering_score = 0
            flags = []
            
            # Check for low sharpness
            if laplacian_var < 100:
                tampering_score += 25
                flags.append("Low image sharpness (possible blur/editing)")
            
            # Check for unusual saturation
            if sat_var > 5000:
                tampering_score += 20
                flags.append("Unusual color saturation")
            
            # Check for high noise
            if noise_sigma > 50:
                tampering_score += 15
                flags.append("High noise levels")
            
            # Check for inconsistent edges
            if edge_variance < 100:
                tampering_score += 10
                flags.append("Low edge consistency")
            
            return {
                "tampering_score": min(100, tampering_score),
                "risk_level": "HIGH" if tampering_score > 60 else "MEDIUM" if tampering_score > 30 else "LOW",
                "flags": flags,
                "metrics": {
                    "laplacian_var": float(laplacian_var),
                    "edge_variance": float(edge_variance),
                    "saturation_variance": float(sat_var),
                    "noise_sigma": float(noise_sigma)
                }
            }
        
        except Exception as e:
            logger.error(f"Error detecting tampering: {str(e)}")
            return {"error": str(e)}
    
    def _estimate_noise(self, image: np.ndarray) -> float:
        """Estimate noise in image"""
        try:
            # Apply Laplacian filter
            laplacian = cv2.Laplacian(image, cv2.CV_64F)
            noise_sigma = np.std(laplacian)
            return noise_sigma
        except:
            return 0
    
    # ========== FIELD VALIDATION ==========
    
    def validate_fields(self, fields: Dict[str, str]) -> Dict:
        """Validate extracted fields"""
        validation_issues = []
        valid_count = 0
        
        for field_name, field_value in fields.items():
            if not field_value:
                validation_issues.append(f"{field_name}: Missing")
                continue
            
            # Basic validation
            if len(str(field_value).strip()) < 2:
                validation_issues.append(f"{field_name}: Too short")
                continue
            
            valid_count += 1
        
        return {
            "overall_valid": len(validation_issues) == 0,
            "valid_fields": valid_count,
            "invalid_fields": len(validation_issues),
            "issues": validation_issues
        }
    
    # ========== FRAUD SCORING ==========
    
    def calculate_fraud_score(self,
                              tampering: Dict,
                              duplicates: Dict,
                              validation: Dict,
                              field_consistency: Dict = None) -> Dict:
        """Calculate overall fraud score"""
        
        score = 0
        risk_factors = []
        
        # Tampering detection (40%)
        tampering_score = tampering.get("tampering_score", 0)
        score += tampering_score * 0.4
        if tampering_score > 30:
            risk_factors.extend(tampering.get("flags", []))
        
        # Duplicate detection (35%)
        if duplicates.get("is_duplicate"):
            score += 35
            risk_factors.append("Possible duplicate submission")
        
        # Field validation (25%)
        if not validation.get("overall_valid"):
            invalid_count = validation.get("invalid_fields", 0)
            score += min(25, invalid_count * 8)
            risk_factors.extend(validation.get("issues", []))
        
        final_score = min(100, score)
        
        # Classify risk
        if final_score >= 80:
            risk_level = "CRITICAL"
        elif final_score >= 60:
            risk_level = "HIGH"
        elif final_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        logger.info(f"Fraud score calculated: {final_score} ({risk_level})")
        
        return {
            "fraud_score": round(final_score, 2),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "confidence": 100 - abs(final_score - 50) / 50 * 20,
            "requires_review": final_score > 40
        }