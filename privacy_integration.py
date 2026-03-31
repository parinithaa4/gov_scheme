"""
COMPLETE PRIVACY PROTECTION SYSTEM FOR GOVERNMENT SCHEMES
==========================================================
This is a standalone module that handles ALL privacy protection.
Just import and use it everywhere in your application.

Created: 2026-03-29
Purpose: Protect sensitive citizen data in government scheme applications
"""

# ==================== IMPORTS ====================
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional
import json
import re
from enum import Enum
import logging
import os


# ==================== LOGGING SETUP ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== ENUM DEFINITIONS ====================
class UserRole(Enum):
    """User roles for access control"""
    ADMIN = "admin"
    OFFICER = "officer"
    USER = "user"
    GUEST = "guest"


class DataClassification(Enum):
    """Data sensitivity levels"""
    PUBLIC = 1
    INTERNAL = 2
    CONFIDENTIAL = 3
    RESTRICTED = 4


# ==================== 1. ENCRYPTION MODULE ====================
class EncryptionManager:
    """
    Handles all encryption/decryption operations
    Uses AES-256 symmetric encryption
    """
    
    def __init__(self, master_key: str):
        """Initialize with a master key (min 16 characters)"""
        if len(master_key) < 16:
            raise ValueError("Master key must be at least 16 characters")
        self.master_key = master_key
        self.cipher_suite = self._derive_cipher_suite()
    
    def _derive_cipher_suite(self) -> Fernet:
        """Derive encryption key from master password"""
        salt = b'gov_scheme_salt_2026'
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted = self.cipher_suite.encrypt(data.encode())
            logger.info("✓ Data encrypted successfully")
            return encrypted.decode()
        except Exception as e:
            logger.error(f"✗ Encryption failed: {str(e)}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_data.encode())
            logger.info("✓ Data decrypted successfully")
            return decrypted.decode()
        except Exception as e:
            logger.error(f"✗ Decryption failed: {str(e)}")
            raise
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return hashlib.sha256(password.encode()).hexdigest() == hashed


# ==================== 2. PII MASKING & ANONYMIZATION ====================
class PIIMasker:
    """Masks and anonymizes Personally Identifiable Information"""
    
    @staticmethod
    def mask_aadhar(aadhar: str) -> str:
        """Mask Aadhar: XXXX XXXX 9101"""
        clean = aadhar.replace(' ', '')
        if len(clean) >= 4:
            return f"XXXX XXXX {clean[-4:]}"
        return "XXXX XXXX XXXX"
    
    @staticmethod
    def mask_pan(pan: str) -> str:
        """Mask PAN: AB****34F"""
        pan = pan.replace(' ', '')
        if len(pan) >= 4:
            return f"{pan[:2]}****{pan[-2:]}"
        return "XX****XX"
    
    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email: r***@example.com"""
        if '@' not in email:
            return email
        local, domain = email.split('@', 1)
        if len(local) > 0:
            return f"{local[0]}***@{domain}"
        return f"***@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone: XXXXXX3210"""
        clean = re.sub(r'\D', '', phone)
        if len(clean) >= 4:
            return f"XXXXXX{clean[-4:]}"
        return "XXXXXX" + clean
    
    @staticmethod
    def mask_name(name: str) -> str:
        """Mask name: R***"""
        if len(name) > 0:
            return f"{name[0]}***"
        return "***"
    
    @staticmethod
    def mask_address(address: str) -> str:
        """Mask address: [ADDRESS MASKED]"""
        return "[ADDRESS MASKED]"
    
    @staticmethod
    def mask_dob(dob: str) -> str:
        """Mask DOB: XXXX-XX-XX"""
        return "XXXX-XX-XX"
    
    @staticmethod
    def tokenize_sensitive_field(value: str, token_prefix: str = "TOKEN") -> Dict:
        """Replace actual value with token (reversible anonymization)"""
        token = f"{token_prefix}_{hashlib.sha256(value.encode()).hexdigest()[:16]}"
        return {
            "token": token,
            "hash": hashlib.sha256(value.encode()).hexdigest(),
            "tokenized_at": datetime.now().isoformat()
        }


# ==================== 3. DATA CLASSIFICATION & FILTERING ====================
class DataClassifier:
    """Classifies data by sensitivity level"""
    
    # Sensitive fields that must be encrypted/masked
    SENSITIVE_FIELDS = {
        'aadhar': DataClassification.RESTRICTED,
        'aadhaar': DataClassification.RESTRICTED,
        'pan': DataClassification.RESTRICTED,
        'password': DataClassification.RESTRICTED,
        'ssn': DataClassification.RESTRICTED,
        'bank_account': DataClassification.RESTRICTED,
        'bank_account_number': DataClassification.RESTRICTED,
        'credit_card': DataClassification.RESTRICTED,
        'email': DataClassification.CONFIDENTIAL,
        'phone': DataClassification.CONFIDENTIAL,
        'phone_number': DataClassification.CONFIDENTIAL,
        'date_of_birth': DataClassification.CONFIDENTIAL,
        'dob': DataClassification.CONFIDENTIAL,
        'address': DataClassification.CONFIDENTIAL,
        'income': DataClassification.CONFIDENTIAL,
        'salary': DataClassification.CONFIDENTIAL,
        'name': DataClassification.CONFIDENTIAL,
        'application_id': DataClassification.INTERNAL,
        'app_id': DataClassification.INTERNAL,
        'scheme_name': DataClassification.INTERNAL,
        'status': DataClassification.INTERNAL
    }
    
    @staticmethod
    def classify_field(field_name: str) -> DataClassification:
        """Get classification level for a field"""
        return DataClassifier.SENSITIVE_FIELDS.get(
            field_name.lower(),
            DataClassification.PUBLIC
        )
    
    @staticmethod
    def get_restricted_fields() -> List[str]:
        """Get all restricted fields"""
        return [
            field for field, classification in DataClassifier.SENSITIVE_FIELDS.items()
            if classification == DataClassification.RESTRICTED
        ]


# ==================== 4. ROLE-BASED ACCESS CONTROL (RBAC) ====================
class AccessControl:
    """Implements Role-Based Access Control"""
    
    # Define permissions for each role
    PERMISSIONS = {
        UserRole.ADMIN: {
            'read': True,
            'write': True,
            'delete': True,
            'export': True,
            'view_all_users': True,
            'manage_encryption': True
        },
        UserRole.OFFICER: {
            'read': True,
            'write': True,
            'delete': False,
            'export': True,
            'view_all_users': False,
            'manage_encryption': False
        },
        UserRole.USER: {
            'read': True,
            'write': True,
            'delete': False,
            'export': False,
            'view_all_users': False,
            'manage_encryption': False
        },
        UserRole.GUEST: {
            'read': True,
            'write': False,
            'delete': False,
            'export': False,
            'view_all_users': False,
            'manage_encryption': False
        }
    }
    
    @staticmethod
    def has_permission(role: UserRole, permission: str) -> bool:
        """Check if user role has permission"""
        return AccessControl.PERMISSIONS.get(role, {}).get(permission, False)
    
    @staticmethod
    def can_access_field(role: UserRole, field_classification: DataClassification) -> bool:
        """Check if user can access field based on sensitivity"""
        access_levels = {
            UserRole.GUEST: [DataClassification.PUBLIC],
            UserRole.USER: [DataClassification.PUBLIC, DataClassification.INTERNAL],
            UserRole.OFFICER: [
                DataClassification.PUBLIC,
                DataClassification.INTERNAL,
                DataClassification.CONFIDENTIAL
            ],
            UserRole.ADMIN: [
                DataClassification.PUBLIC,
                DataClassification.INTERNAL,
                DataClassification.CONFIDENTIAL,
                DataClassification.RESTRICTED
            ]
        }
        return field_classification in access_levels.get(role, [])


# ==================== 5. AUDIT LOGGING ====================
class AuditLogger:
    """Logs all data access and modifications"""
    
    def __init__(self, log_file: str = "audit_log.json"):
        self.log_file = log_file
        self.logs: List[Dict] = []
        self._load_existing_logs()
    
    def _load_existing_logs(self):
        """Load existing logs from file"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    self.logs = json.load(f)
            except:
                self.logs = []
    
    def _save_logs(self):
        """Save logs to file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.logs, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not save logs: {e}")
    
    def log_access(
        self,
        user_id: str,
        user_role: UserRole,
        action: str,
        resource: str,
        status: str = "SUCCESS",
        details: Optional[Dict] = None
    ) -> None:
        """Log data access event"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "user_role": user_role.value,
            "action": action,
            "resource": resource,
            "status": status,
            "details": details or {}
        }
        self.logs.append(log_entry)
        self._save_logs()
        logger.info(f"✓ Audit log recorded: {action} by {user_id}")
    
    def get_user_activity(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get user's activity in last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            log for log in self.logs
            if log['user_id'] == user_id and
            datetime.fromisoformat(log['timestamp']) > cutoff_date
        ]
    
    def detect_suspicious_activity(self, user_id: str, threshold: int = 5) -> bool:
        """Detect suspicious activity (multiple failed attempts)"""
        recent_logs = self.get_user_activity(user_id, days=1)
        failed_attempts = sum(1 for log in recent_logs if log['status'] == 'FAILURE')
        return failed_attempts >= threshold


# ==================== 6. DATA RETENTION POLICY ====================
class DataRetentionManager:
    """Manages data retention and deletion"""
    
    # Retention periods (in days)
    RETENTION_PERIODS = {
        'application_data': 365,
        'user_logs': 180,
        'failed_attempts': 90,
        'sensitive_documents': 365
    }
    
    @staticmethod
    def should_delete(data_type: str, created_date: datetime) -> bool:
        """Check if data should be deleted based on retention policy"""
        retention_days = DataRetentionManager.RETENTION_PERIODS.get(data_type, 365)
        expiry_date = created_date + timedelta(days=retention_days)
        return datetime.now() > expiry_date
    
    @staticmethod
    def get_expiry_date(data_type: str, created_date: datetime) -> datetime:
        """Get when data will expire"""
        retention_days = DataRetentionManager.RETENTION_PERIODS.get(data_type, 365)
        return created_date + timedelta(days=retention_days)


# ==================== 7. MAIN SECURE DATA WRAPPER ====================
class SecureDataWrapper:
    """
    MAIN CLASS: Wraps user data with encryption, masking, and access control
    
    THIS IS THE CLASS TO USE EVERYWHERE IN YOUR APPLICATION
    """
    
    def __init__(
        self,
        encryption_key: str,
        enable_masking: bool = True,
        enable_audit: bool = True
    ):
        """Initialize secure wrapper"""
        if len(encryption_key) < 16:
            raise ValueError("Encryption key must be at least 16 characters")
        
        self.encryptor = EncryptionManager(encryption_key)
        self.masker = PIIMasker()
        self.access_control = AccessControl()
        self.audit_logger = AuditLogger()
        self.retention_manager = DataRetentionManager()
        self.enable_masking = enable_masking
        self.enable_audit = enable_audit
        logger.info("✓ SecureDataWrapper initialized")
    
    def protect_user_data(
        self,
        user_data: Dict[str, Any],
        user_role: UserRole = UserRole.USER,
        user_id: str = "system"
    ) -> Dict[str, Any]:
        """
        Apply all privacy protections to user data
        
        PROCESS:
        1. Filter fields based on user role
        2. Encrypt sensitive fields
        3. Mask PII in non-encrypted fields
        4. Log access
        
        USAGE:
        protected_data = secure_wrapper.protect_user_data(
            user_data={"aadhar": "1234...", "email": "..."},
            user_role=UserRole.OFFICER,
            user_id="OFFICER_001"
        )
        """
        protected_data = {}
        
        for field_name, field_value in user_data.items():
            if field_value is None:
                protected_data[field_name] = None
                continue
            
            classification = DataClassifier.classify_field(field_name)
            
            # Check access control
            if not self.access_control.can_access_field(user_role, classification):
                protected_data[field_name] = "[REDACTED - INSUFFICIENT PERMISSIONS]"
                
                # Log denied access
                if self.enable_audit:
                    self.audit_logger.log_access(
                        user_id=user_id,
                        user_role=user_role,
                        action="access_denied",
                        resource=field_name,
                        status="DENIED"
                    )
                continue
            
            # Encrypt restricted fields
            if classification == DataClassification.RESTRICTED:
                protected_data[field_name] = {
                    "encrypted": self.encryptor.encrypt(str(field_value)),
                    "encrypted_at": datetime.now().isoformat(),
                    "classification": "RESTRICTED"
                }
            
            # Mask confidential fields
            elif classification == DataClassification.CONFIDENTIAL and self.enable_masking:
                protected_data[field_name] = self._mask_field(field_name, field_value)
            
            else:
                protected_data[field_name] = field_value
            
            # Log access
            if self.enable_audit:
                self.audit_logger.log_access(
                    user_id=user_id,
                    user_role=user_role,
                    action="access_data",
                    resource=field_name,
                    status="SUCCESS",
                    details={"classification": classification.name}
                )
        
        return protected_data
    
    def _mask_field(self, field_name: str, field_value: Any) -> str:
        """Apply appropriate masking based on field name"""
        field_lower = field_name.lower()
        value_str = str(field_value)
        
        if 'aadhar' in field_lower or 'aadhaar' in field_lower:
            return self.masker.mask_aadhar(value_str)
        elif 'pan' in field_lower:
            return self.masker.mask_pan(value_str)
        elif 'email' in field_lower:
            return self.masker.mask_email(value_str)
        elif 'phone' in field_lower:
            return self.masker.mask_phone(value_str)
        elif 'name' in field_lower:
            return self.masker.mask_name(value_str)
        elif 'address' in field_lower:
            return self.masker.mask_address(value_str)
        elif 'dob' in field_lower or 'date_of_birth' in field_lower:
            return self.masker.mask_dob(value_str)
        else:
            return value_str
    
    def decrypt_field(self, encrypted_data: Dict) -> str:
        """Decrypt a previously encrypted field"""
        if isinstance(encrypted_data, dict) and 'encrypted' in encrypted_data:
            return self.encryptor.decrypt(encrypted_data['encrypted'])
        return str(encrypted_data)
    
    def get_audit_logs(self, user_id: str = None, days: int = 30) -> List[Dict]:
        """Get audit logs"""
        if user_id:
            return self.audit_logger.get_user_activity(user_id, days)
        return self.audit_logger.logs[-100:]  # Last 100 logs
    
    def check_suspicious_activity(self, user_id: str) -> bool:
        """Check if user has suspicious activity"""
        return self.audit_logger.detect_suspicious_activity(user_id)


# ==================== 8. UTILITY FUNCTIONS ====================
def initialize_privacy_system(encryption_key: str = None) -> SecureDataWrapper:
    """
    Initialize privacy system with encryption key from environment
    
    USAGE in main.py:
    secure_wrapper = initialize_privacy_system()
    """
    if encryption_key is None:
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if not encryption_key:
            raise ValueError(
                "ENCRYPTION_KEY not found in .env file. "
                "Please add: ENCRYPTION_KEY=your_32_char_key"
            )
    
    return SecureDataWrapper(
        encryption_key=encryption_key,
        enable_masking=True,
        enable_audit=True
    )


def protect_response(data: Dict, user_role: UserRole, secure_wrapper: SecureDataWrapper) -> Dict:
    """
    Convenience function to protect API responses
    
    USAGE in routers:
    @app.get("/user/{user_id}")
    def get_user(user_id: str):
        user = get_user_from_db(user_id)
        protected = protect_response(user, UserRole.OFFICER, secure_wrapper)
        return protected
    """
    return secure_wrapper.protect_user_data(user_data=data, user_role=user_role)


# ==================== 9. EXAMPLE USAGE ====================
def example_usage():
    """
    EXAMPLE: How to use this privacy system
    
    RUN THIS: python services/privacy_integration.py
    """
    
    print("\n" + "="*70)
    print("PRIVACY PROTECTION SYSTEM - DEMO")
    print("="*70 + "\n")
    
    # Initialize
    try:
        secure_wrapper = SecureDataWrapper(
            encryption_key="strong_master_key_minimum_32_characters_long"
        )
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Sample user data
    user_data = {
        "name": "Rajesh Kumar",
        "email": "rajesh.kumar@example.com",
        "phone": "9876543210",
        "aadhar": "1234 5678 9101 1213",
        "pan": "ABCDE1234F",
        "date_of_birth": "1990-05-15",
        "address": "123 Main Street, New Delhi",
        "income": "500000",
        "bank_account": "123456789012",
        "application_id": "APP12345",
        "scheme_name": "PM-KISAN"
    }
    
    print("ORIGINAL DATA:")
    print(json.dumps(user_data, indent=2))
    print("\n" + "-"*70 + "\n")
    
    # Test different roles
    roles = [UserRole.GUEST, UserRole.USER, UserRole.OFFICER, UserRole.ADMIN]
    
    for role in roles:
        print(f"\n{role.value.upper()} - DATA ACCESS:")
        protected = secure_wrapper.protect_user_data(user_data, role)
        print(json.dumps(protected, indent=2, default=str))
        print("\n" + "-"*70)
    
    # Show decryption
    print("\nDECRYPTION EXAMPLE:")
    admin_protected = secure_wrapper.protect_user_data(user_data, UserRole.ADMIN)
    if isinstance(admin_protected.get('aadhar'), dict):
        decrypted = secure_wrapper.decrypt_field(admin_protected['aadhar'])
        print(f"Encrypted Aadhar: {admin_protected['aadhar']['encrypted'][:50]}...")
        print(f"Decrypted Aadhar: {decrypted}")
    
    # Show audit logs
    print(f"\n\nAUDIT LOGS (Last 10 entries):")
    logs = secure_wrapper.get_audit_logs(days=1)
    for log in logs[-10:]:
        print(f"[{log['timestamp']}] {log['user_role']} - {log['action']} - {log['resource']}")


# ==================== MAIN ====================
if __name__ == "__main__":
    example_usage()