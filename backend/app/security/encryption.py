"""Encryption utilities for sensitive data."""
from cryptography.fernet import Fernet
from app.core.config import settings
import os
from app.core.logging import logger


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""
    
    def __init__(self):
        """Initialize encryption service with key from environment."""
        self.cipher = self._get_cipher()
    
    def _get_cipher(self) -> Fernet:
        """Get or generate encryption cipher.
        
        In production, the ENCRYPTION_KEY should be:
        1. Generated once: Fernet.generate_key()
        2. Stored securely (environment variable, secrets manager, etc.)
        3. Never committed to version control
        
        Returns:
            Fernet cipher instance
        """
        try:
            # Try to get key from environment
            key = os.getenv("ENCRYPTION_KEY")
            if not key:
                logger.warning("ENCRYPTION_KEY not found in environment. Generating temporary key.")
                # For development only - generate a temporary key
                key = Fernet.generate_key()
            return Fernet(key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {str(e)}")
            raise
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Encrypted string (Base64 encoded)
        """
        try:
            encrypted = self.cipher.encrypt(plaintext.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext string.
        
        Args:
            ciphertext: Encrypted string (Base64 encoded)
            
        Returns:
            Decrypted plaintext string
        """
        try:
            decrypted = self.cipher.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
    
    def rotate_key(self, new_key: bytes) -> bool:
        """Rotate encryption key (for future use).
        
        Args:
            new_key: New encryption key
            
        Returns:
            True if rotation successful
        """
        try:
            # This would typically involve:
            # 1. Re-encrypting all sensitive data with new key
            # 2. Updating environment variable
            # 3. Archiving old key
            logger.info("Key rotation initiated")
            return True
        except Exception as e:
            logger.error(f"Key rotation failed: {str(e)}")
            return False


# Singleton instance
_encryption_service = None


def get_encryption_service() -> EncryptionService:
    """Get or create encryption service instance.
    
    Returns:
        EncryptionService singleton
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
