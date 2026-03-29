"""
Document Processor Service
Orchestrates OCR, fraud detection, and validation for complete document processing
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime
from ocr_fraud_detection import DocumentProcessor as BaseProcessor
from image_utils import ImageUtils
from validation_utils import ValidationUtils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedDocumentProcessor:
    """Advanced document processor with enhanced features"""
    
    def __init__(self):
        """Initialize processor with all services"""
        self.base_processor = BaseProcessor()
        self.image_utils = ImageUtils()
        self.validation_utils = ValidationUtils()
        logger.info("AdvancedDocumentProcessor initialized")
    
    def process_document_complete(self,
                                  image_path: str,
                                  document_type: str,
                                  stored_hashes: Optional[List[Dict]] = None,
                                  db_records: Optional[List[Dict]] = None,
                                  save_preprocessed: bool = False) -> Dict:
        """
        Complete document processing with all validations
        
        Args:
            image_path: Path to document image
            document_type: Type of document
            stored_hashes: Previously stored hashes
            db_records: Database records for comparison
            save_preprocessed: Save preprocessed image
            
        Returns:
            Complete analysis report
        """
        
        logger.info(f"Starting advanced document processing: {image_path}")
        
        try:
            # ============ VALIDATION ============
            is_valid_type, type_msg = self.validation_utils.validate_document_type(document_type)
            if not is_valid_type:
                return {
                    "status": "error",
                    "error": type_msg,
                    "timestamp": datetime.now().isoformat()
                }
            
            # ============ IMAGE ANALYSIS ============
            logger.info("Getting image information...")
            image_info = self.image_utils.get_image_info(image_path)
            
            # ============ IMAGE PREPROCESSING ============
            logger.info("Preprocessing image for OCR...")
            preprocessed_img = self.image_utils.preprocess_for_ocr(image_path)
            
            if preprocessed_img is None:
                return {
                    "status": "error",
                    "error": "Failed to preprocess image",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Save preprocessed image if requested
            if save_preprocessed:
                preprocessed_path = image_path.replace('.', '_preprocessed.')
                self.image_utils.save_image(preprocessed_img, preprocessed_path)
                logger.info(f"Preprocessed image saved: {preprocessed_path}")
            
            # ============ OCR & FRAUD DETECTION ============
            logger.info("Running OCR and fraud detection...")
            base_report = self.base_processor.process_document(
                image_path=image_path,
                document_type=document_type,
                stored_hashes=stored_hashes or [],
                db_records=db_records or []
            )
            
            # ============ ADVANCED FIELD VALIDATION ============
            logger.info("Performing advanced field validation...")
            extracted_fields = base_report["extracted_fields"]
            field_validation = self.validation_utils.validate_extracted_fields(extracted_fields)
            
            # ============ SUSPICIOUS PATTERN DETECTION ============
            logger.info("Checking for suspicious patterns...")
            ocr_text = base_report["ocr_analysis"]["extracted_text"]
            suspicious_patterns = self.validation_utils.check_suspicious_patterns(ocr_text)
            
            # ============ IMAGE STATISTICS ============
            logger.info("Calculating image statistics...")
            image_stats = self.image_utils.get_image_statistics(preprocessed_img)
            
            # ============ COMPREHENSIVE REPORT ============
            comprehensive_report = {
                "status": "success",
                "document_type": document_type,
                "processed_at": datetime.now().isoformat(),
                
                # Image Analysis
                "image_analysis": {
                    "file_info": image_info,
                    "image_statistics": image_stats,
                    "tampering_score": base_report["image_analysis"]["tampering_score"],
                    "tampering_risk": base_report["image_analysis"]["tampering_risk"],
                    "tampering_flags": base_report["image_analysis"]["flags"]
                },
                
                # OCR Results
                "ocr_analysis": {
                    "extracted_text": base_report["ocr_analysis"]["extracted_text"],
                    "confidence": base_report["ocr_analysis"]["confidence"],
                    "method": base_report["ocr_analysis"]["method"]
                },
                
                # Extracted Fields
                "extracted_fields": extracted_fields,
                
                # Field Validation (Enhanced)
                "field_validation": {
                    "overall_valid": field_validation["overall_valid"],
                    "total_fields": field_validation["total_fields"],
                    "valid_fields": field_validation["valid_fields"],
                    "invalid_fields": field_validation["invalid_fields"],
                    "missing_fields": field_validation["missing_fields"],
                    "issues": field_validation["issues"],
                    "detailed_results": field_validation["detailed_results"]
                },
                
                # Suspicious Patterns
                "suspicious_patterns": {
                    "patterns_found": len(suspicious_patterns) > 0,
                    "patterns": suspicious_patterns
                },
                
                # Fraud Analysis
                "fraud_analysis": {
                    "fraud_score": base_report["fraud_analysis"]["fraud_score"],
                    "risk_level": base_report["fraud_analysis"]["risk_level"],
                    "recommendation": base_report["fraud_analysis"]["recommendation"],
                    "requires_manual_review": base_report["fraud_analysis"]["requires_manual_review"],
                    "risk_factors": base_report["fraud_analysis"]["risk_factors"]
                },
                
                # Duplicate Detection
                "duplicate_check": {
                    "is_duplicate": base_report["duplicate_check"]["is_duplicate"],
                    "duplicates_found": base_report["duplicate_check"]["duplicates_found"]
                },
                
                # Image Hashes
                "image_hashes": base_report["image_hashes"],
                
                # Final Assessment
                "final_assessment": self._generate_final_assessment(
                    base_report,
                    field_validation,
                    suspicious_patterns,
                    image_stats
                )
            }
            
            logger.info(f"Document processing completed successfully")
            return comprehensive_report
        
        except Exception as e:
            logger.error(f"Error in advanced document processing: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_final_assessment(self,
                                   base_report: Dict,
                                   field_validation: Dict,
                                   suspicious_patterns: List[str],
                                   image_stats: Dict) -> Dict:
        """
        Generate final assessment and recommendation
        
        Args:
            base_report: Base fraud detection report
            field_validation: Field validation results
            suspicious_patterns: Detected suspicious patterns
            image_stats: Image statistics
            
        Returns:
            Final assessment dictionary
        """
        
        overall_score = 0
        risk_factors = []
        
        # Fraud score (50% weight)
        fraud_score = base_report["fraud_analysis"]["fraud_score"]
        overall_score += fraud_score * 0.5
        
        # Field validation issues (30% weight)
        invalid_field_count = field_validation["invalid_fields"] + field_validation["missing_fields"]
        field_score = min(100, invalid_field_count * 10)
        overall_score += field_score * 0.3
        risk_factors.extend(field_validation["issues"])
        
        # Suspicious patterns (20% weight)
        pattern_score = len(suspicious_patterns) * 15
        overall_score += min(100, pattern_score) * 0.2
        risk_factors.extend(suspicious_patterns)
        
        overall_score = min(100, overall_score)
        
        # Determine final recommendation
        if overall_score >= 80:
            recommendation = "STRONGLY REJECT - High probability of fraud or document issues"
            action = "reject"
        elif overall_score >= 60:
            recommendation = "REJECT - Significant issues detected, manual review recommended"
            action = "reject"
        elif overall_score >= 40:
            recommendation = "REVIEW REQUIRED - Document needs manual verification"
            action = "review"
        elif overall_score >= 20:
            recommendation = "CONDITIONAL APPROVAL - Request additional documents"
            action = "conditional"
        else:
            recommendation = "APPROVE - Document appears authentic and complete"
            action = "approve"
        
        return {
            "overall_score": round(overall_score, 2),
            "risk_level": self._classify_overall_risk(overall_score),
            "recommendation": recommendation,
            "action": action,
            "confidence": 100 - (abs(overall_score - 50) / 50 * 20),
            "key_risk_factors": risk_factors[:5]  # Top 5 risk factors
        }
    
    def _classify_overall_risk(self, score: float) -> str:
        """Classify overall risk level"""
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        elif score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def batch_process_documents(self,
                               image_paths: List[str],
                               document_type: str,
                               stored_hashes: Optional[List[Dict]] = None,
                               db_records: Optional[List[Dict]] = None) -> Dict:
        """
        Process multiple documents in batch
        
        Args:
            image_paths: List of image paths
            document_type: Type of documents
            stored_hashes: Stored hashes for comparison
            db_records: Database records
            
        Returns:
            Batch processing report
        """
        
        logger.info(f"Starting batch processing of {len(image_paths)} documents")
        
        results = []
        statistics = {
            "total": len(image_paths),
            "processed": 0,
            "failed": 0,
            "approved": 0,
            "rejected": 0,
            "review_required": 0,
            "average_fraud_score": 0,
            "average_confidence": 0
        }
        
        total_fraud_score = 0
        total_confidence = 0
        
        for i, image_path in enumerate(image_paths, 1):
            try:
                logger.info(f"Processing {i}/{len(image_paths)}: {image_path}")
                
                report = self.process_document_complete(
                    image_path=image_path,
                    document_type=document_type,
                    stored_hashes=stored_hashes,
                    db_records=db_records
                )
                
                if report["status"] == "success":
                    statistics["processed"] += 1
                    
                    action = report["final_assessment"]["action"]
                    if action == "approve":
                        statistics["approved"] += 1
                    elif action == "reject":
                        statistics["rejected"] += 1
                    else:
                        statistics["review_required"] += 1
                    
                    total_fraud_score += report["fraud_analysis"]["fraud_score"]
                    total_confidence += report["final_assessment"]["confidence"]
                    
                    results.append({
                        "file": image_path,
                        "status": "success",
                        "fraud_score": report["fraud_analysis"]["fraud_score"],
                        "risk_level": report["fraud_analysis"]["risk_level"],
                        "action": action
                    })
                else:
                    statistics["failed"] += 1
                    results.append({
                        "file": image_path,
                        "status": "failed",
                        "error": report.get("error", "Unknown error")
                    })
            
            except Exception as e:
                logger.error(f"Error processing {image_path}: {str(e)}")
                statistics["failed"] += 1
                results.append({
                    "file": image_path,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Calculate averages
        if statistics["processed"] > 0:
            statistics["average_fraud_score"] = round(total_fraud_score / statistics["processed"], 2)
            statistics["average_confidence"] = round(total_confidence / statistics["processed"], 2)
        
        logger.info(f"Batch processing completed: {statistics}")
        
        return {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "statistics": statistics,
            "results": results
        }