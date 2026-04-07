"""
Token Encryption Utility

Encrypts and decrypts sensitive broker API tokens before storing in MongoDB.
"""

from cryptography.fernet import Fernet
import os
import logging

logger = logging.getLogger(__name__)


class TokenEncryption:
    """Handles encryption and decryption of sensitive tokens"""
    
    def __init__(self):
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if not encryption_key:
            logger.warning("ENCRYPTION_KEY not found in environment variables")
            # Generate a temporary key for development (NOT for production!)
            encryption_key = Fernet.generate_key().decode()
            logger.warning(f"Using temporary encryption key: {encryption_key}")
        
        self.cipher = Fernet(encryption_key.encode())
    
    def encrypt(self, token: str) -> str:
        """Encrypt a token string"""
        if not token:
            return ""
        try:
            encrypted = self.cipher.encrypt(token.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_token: str) -> str:
        """Decrypt an encrypted token"""
        if not encrypted_token:
            return ""
        try:
            decrypted = self.cipher.decrypt(encrypted_token.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise


# Global instance
token_encryption = TokenEncryption()
