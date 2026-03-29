"""
Validation Utilities Service
Handles field validation, format checking, and data verification
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, date
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation status enum"""
    VALID = "valid"
    INVALID = "invalid"
    SUSPICIOUS = "suspicious"
    MISSING = "missing"


class ValidationUtils:
    """Utility class for data validation"""
    
    # Regular expressions for common patterns
    PATTERNS = {
        'email': r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$',
        'phone_india': r'^(\+91[-.\s]?)?[0-9]{10}$',
        'phone_international': r'^\+[1-9]\d{1,14}$',
        'name': r'^[a-zA-Z\s\'-]{3,100}$',
        'aadhaar': r'^[0-9]{12}$',
        'pan': r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$',
        'voter_id': r'^[A-Z]{3}[0-9]{7}$',
        'driving_license': r'^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{7}$',
        'passport': r'^[A-Z]{1}[0-9]{7}$',
        'date_ddmmyyyy': r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[012])-(\d{4})$',
        'date_yyyymmdd': r'^(\d{4})-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])$',
        'postal_code_india': r'^[0-9]{6}$',
        'url': r'^https?:\/\/.+$',
        'alphanumeric': r'^[a-zA-Z0-9]+$',
    }
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email address
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not email:
            return False, "Email is empty"
        
        if not re.match(ValidationUtils.PATTERNS['email'], email):
            return False, "Invalid email format"
        
        if len(email) > 255:
            return False, "Email too long"
        
        logger.info(f"Email validated: {email}")
        return True, "Valid email"
    
    @staticmethod
    def validate_phone(phone: str, country: str = "IN") -> Tuple[bool, str]:
        """
        Validate phone number
        
        Args:
            phone: Phone number to validate
            country: Country code (default: IN for India)
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not phone:
            return False, "Phone is empty"
        
        # Remove common separators
        phone = re.sub(r'[\s\-\.]', '', phone)
        
        if country == "IN":
            if not re.match(r'^(\+91)?[0-9]{10}$', phone):
                return False, "Invalid Indian phone number"
        else:
            if not re.match(ValidationUtils.PATTERNS['phone_international'], phone):
                return False, "Invalid international phone number"
        
        logger.info(f"Phone validated: {phone}")
        return True, "Valid phone number"
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """
        Validate person's name
        
        Args:
            name: Name to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not name:
            return False, "Name is empty"
        
        name = name.strip()
        
        if len(name) < 3:
            return False, "Name too short (minimum 3 characters)"
        
        if len(name) > 100:
            return False, "Name too long (maximum 100 characters)"
        
        if not re.match(ValidationUtils.PATTERNS['name'], name):
            return False, "Name contains invalid characters"
        
        logger.info(f"Name validated: {name}")
        return True, "Valid name"
    
    @staticmethod
    def validate_aadhaar(aadhaar: str) -> Tuple[bool, str]:
        """
        Validate Aadhaar number (India)
        
        Args:
            aadhaar: Aadhaar number
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not aadhaar:
            return False, "Aadhaar is empty"
        
        aadhaar = re.sub(r'\s', '', aadhaar)
        
        if not re.match(ValidationUtils.PATTERNS['aadhaar'], aadhaar):
            return False, "Invalid Aadhaar format (must be 12 digits)"
        
        # Verhoeff algorithm for checksum (simplified)
        if not ValidationUtils._verify_aadhaar_checksum(aadhaar):
            return False, "Invalid Aadhaar checksum"
        
        logger.info(f"Aadhaar validated: {aadhaar}")
        return True, "Valid Aadhaar"
    
    @staticmethod
    def _verify_aadhaar_checksum(aadhaar: str) -> bool:
        """
        Verify Aadhaar checksum using Verhoeff algorithm
        
        Args:
            aadhaar: 12-digit Aadhaar number
            
        Returns:
            True if checksum is valid
        """
        # Simplified check - in production use complete Verhoeff algorithm
        if len(aadhaar) != 12:
            return False
        if not aadhaar.isdigit():
            return False
        return True
    
    @staticmethod
    def validate_pan(pan: str) -> Tuple[bool, str]:
        """
        Validate PAN number (India)
        
        Args:
            pan: PAN number
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not pan:
            return False, "PAN is empty"
        
        pan = pan.upper().strip()
        
        if not re.match(ValidationUtils.PATTERNS['pan'], pan):
            return False, "Invalid PAN format (e.g., ABCDE1234F)"
        
        logger.info(f"PAN validated: {pan}")
        return True, "Valid PAN"
    
    @staticmethod
    def validate_date(date_str: str, format: str = "DD-MM-YYYY") -> Tuple[bool, str]:
        """
        Validate date string
        
        Args:
            date_str: Date string to validate
            format: Expected format (DD-MM-YYYY, YYYY-MM-DD)
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not date_str:
            return False, "Date is empty"
        
        formats = {
            'DD-MM-YYYY': '%d-%m-%Y',
            'YYYY-MM-DD': '%Y-%m-%d',
            'DD/MM/YYYY': '%d/%m/%Y',
            'MM/DD/YYYY': '%m/%d/%Y',
        }
        
        date_format = formats.get(format, '%d-%m-%Y')
        
        try:
            parsed_date = datetime.strptime(date_str.strip(), date_format).date()
            
            # Check if date is not in future
            if parsed_date > date.today():
                return False, "Date cannot be in the future"
            
            # Check if date is reasonable (not more than 150 years ago)
            age = (date.today() - parsed_date).days // 365
            if age > 150:
                return False, "Date seems invalid (person would be over 150 years old)"
            
            logger.info(f"Date validated: {date_str}")
            return True, "Valid date"
        
        except ValueError:
            return False, f"Invalid date format. Expected {format}"
    
    @staticmethod
    def calculate_age(dob: str, format: str = "DD-MM-YYYY") -> Optional[int]:
        """
        Calculate age from date of birth
        
        Args:
            dob: Date of birth string
            format: Date format
            
        Returns:
            Age in years or None if invalid
        """
        try:
            formats = {
                'DD-MM-YYYY': '%d-%m-%Y',
                'YYYY-MM-DD': '%Y-%m-%d',
            }
            
            date_format = formats.get(format, '%d-%m-%Y')
            birth_date = datetime.strptime(dob.strip(), date_format).date()
            today = date.today()
            
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            logger.info(f"Age calculated: {age}")
            return age
        
        except:
            logger.error(f"Error calculating age for DOB: {dob}")
            return None
    
    @staticmethod
    def validate_age(age: int, min_age: int = 0, max_age: int = 150) -> Tuple[bool, str]:
        """
        Validate age range
        
        Args:
            age: Age to validate
            min_age: Minimum valid age
            max_age: Maximum valid age
            
        Returns:
            Tuple of (is_valid, message)
        """
        if age < min_age:
            return False, f"Age must be at least {min_age}"
        
        if age > max_age:
            return False, f"Age cannot exceed {max_age}"
        
        logger.info(f"Age validated: {age}")
        return True, "Valid age"
    
    @staticmethod
    def validate_address(address: str) -> Tuple[bool, str]:
        """
        Validate address
        
        Args:
            address: Address to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not address:
            return False, "Address is empty"
        
        address = address.strip()
        
        if len(address) < 10:
            return False, "Address too short (minimum 10 characters)"
        
        if len(address) > 500:
            return False, "Address too long (maximum 500 characters)"
        
        logger.info(f"Address validated")
        return True, "Valid address"
    
    @staticmethod
    def validate_postal_code(postal_code: str, country: str = "IN") -> Tuple[bool, str]:
        """
        Validate postal/zip code
        
        Args:
            postal_code: Postal code to validate
            country: Country code
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not postal_code:
            return False, "Postal code is empty"
        
        postal_code = re.sub(r'\s', '', postal_code)
        
        if country == "IN":
            if not re.match(ValidationUtils.PATTERNS['postal_code_india'], postal_code):
                return False, "Invalid Indian postal code (must be 6 digits)"
        else:
            if not re.match(r'^\d{5}(-\d{4})?$', postal_code):
                return False, "Invalid postal code format"
        
        logger.info(f"Postal code validated: {postal_code}")
        return True, "Valid postal code"
    
    @staticmethod
    def validate_field_format(field_name: str, field_value: str) -> Tuple[bool, str]:
        """
        Generic field format validation
        
        Args:
            field_name: Name of the field
            field_value: Value to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        field_name_lower = field_name.lower()
        
        if 'email' in field_name_lower:
            return ValidationUtils.validate_email(field_value)
        
        elif 'phone' in field_name_lower or 'mobile' in field_name_lower:
            return ValidationUtils.validate_phone(field_value)
        
        elif 'name' in field_name_lower:
            return ValidationUtils.validate_name(field_value)
        
        elif 'aadhaar' in field_name_lower:
            return ValidationUtils.validate_aadhaar(field_value)
        
        elif 'pan' in field_name_lower:
            return ValidationUtils.validate_pan(field_value)
        
        elif 'date' in field_name_lower or 'dob' in field_name_lower:
            return ValidationUtils.validate_date(field_value)
        
        elif 'address' in field_name_lower:
            return ValidationUtils.validate_address(field_value)
        
        elif 'postal' in field_name_lower or 'zip' in field_name_lower:
            return ValidationUtils.validate_postal_code(field_value)
        
        else:
            return True, "Field format not specifically validated"
    
    @staticmethod
    def validate_extracted_fields(fields: Dict[str, str]) -> Dict[str, any]:
        """
        Validate all extracted fields at once
        
        Args:
            fields: Dictionary of fields
            
        Returns:
            Dictionary with validation results
        """
        results = {}
        issues = []
        
        for field_name, field_value in fields.items():
            if not field_value:
                results[field_name] = {
                    "status": ValidationStatus.MISSING.value,
                    "message": "Field not found"
                }
                issues.append(f"{field_name}: Not found")
                continue
            
            is_valid, message = ValidationUtils.validate_field_format(field_name, field_value)
            
            if is_valid:
                results[field_name] = {
                    "status": ValidationStatus.VALID.value,
                    "message": message,
                    "value": field_value
                }
            else:
                results[field_name] = {
                    "status": ValidationStatus.INVALID.value,
                    "message": message,
                    "value": field_value
                }
                issues.append(f"{field_name}: {message}")
        
        logger.info(f"Field validation completed. Issues: {len(issues)}")
        
        return {
            "overall_valid": len(issues) == 0,
            "total_fields": len(fields),
            "valid_fields": len([r for r in results.values() if r["status"] == ValidationStatus.VALID.value]),
            "invalid_fields": len([r for r in results.values() if r["status"] == ValidationStatus.INVALID.value]),
            "missing_fields": len([r for r in results.values() if r["status"] == ValidationStatus.MISSING.value]),
            "issues": issues,
            "detailed_results": results
        }
    
    @staticmethod
    def check_suspicious_patterns(text: str) -> List[str]:
        """
        Check for suspicious patterns in text
        
        Args:
            text: Text to check
            
        Returns:
            List of suspicious patterns found
        """
        suspicious = []
        
        # Check for repeated characters
        if re.search(r'(.)\1{4,}', text):
            suspicious.append("Repeated characters detected")
        
        # Check for excessive special characters
        if len(re.findall(r'[^a-zA-Z0-9\s\-]', text)) > len(text) * 0.1:
            suspicious.append("Excessive special characters")
        
        # Check for unusual spacing
        if re.search(r'\s{3,}', text):
            suspicious.append("Unusual spacing patterns")
        
        # Check for mixed scripts (potential forgery indicator)
        if re.search(r'[^\x00-\x7F]', text):
            suspicious.append("Non-ASCII characters detected")
        
        if suspicious:
            logger.warning(f"Suspicious patterns found: {suspicious}")
        
        return suspicious
    
    @staticmethod
    def validate_document_type(document_type: str) -> Tuple[bool, str]:
        """
        Validate document type
        
        Args:
            document_type: Type of document
            
        Returns:
            Tuple of (is_valid, message)
        """
        valid_types = [
            'aadhaar', 'pan', 'passport', 'driving_license',
            'voter_id', 'aadhar_letter', 'utility_bill',
            'bank_statement', 'other'
        ]
        
        if document_type.lower() not in valid_types:
            return False, f"Invalid document type. Allowed: {', '.join(valid_types)}"
        
        logger.info(f"Document type validated: {document_type}")
        return True, "Valid document type"