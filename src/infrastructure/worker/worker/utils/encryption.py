from ..settings import settings
from cryptography.hazmat.primitives.keywrap import aes_key_unwrap
from cryptography.fernet import Fernet
import base64


class EncryptionManager:
    """
    Manages encryption and decryption using KEK/DEK pattern.
    
    KEK (Key Encryption Key) - Master key used to unwrap DEKs
    DEK (Data Encryption Key) - Wrapped key used to encrypt actual data
    """
    
    def __init__(self, kek: str):
        """
        Initialize encryption manager with Key Encryption Key.
        
        Args:
            kek: Hexadecimal string representing the KEK
        """
        self.kek = bytes.fromhex(kek)
    
    def decrypt(self, wrapped_dek: bytes, ciphertext: bytes) -> bytes:
        """
        Decrypt data using KEK/DEK unwrapping.
        
        Args:
            wrapped_dek: Wrapped Data Encryption Key
            ciphertext: Encrypted data
            
        Returns:
            Decrypted plaintext as bytes
            
        Example:
            plaintext = encryption_manager.decrypt(
                wrapped_dek=social_account.wrapped_dek,
                ciphertext=social_account.encrypted_credentials
            )
        """
        # Unwrap DEK using KEK
        dek = aes_key_unwrap(self.kek, wrapped_dek)
        
        # Create Fernet instance with DEK
        fernet = Fernet(base64.urlsafe_b64encode(dek))
        
        # Decrypt data
        plaintext = fernet.decrypt(ciphertext)
        
        return plaintext

encryption_manager = EncryptionManager(kek=settings.KEK_KEY)
