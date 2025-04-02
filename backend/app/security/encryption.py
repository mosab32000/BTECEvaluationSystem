from cryptography.fernet import Fernet, InvalidToken
import base64
import logging

class Vault:
    def __init__(self, key):
        if not key:
            logging.error("Encryption key is missing!")
            raise ValueError("ENCRYPTION_KEY environment variable not set.")
        try:
            # Key should be a URL-safe base64-encoded 32-byte key
            self.cipher = Fernet(key)
        except (ValueError, TypeError) as e:
            logging.error(f"Invalid encryption key format: {e}")
            raise ValueError("Invalid ENCRYPTION_KEY format. Ensure it's a valid Fernet key.")

    def encrypt(self, text: str) -> str:
        """Encrypts a string and returns the encrypted string"""
        try:
            return self.cipher.encrypt(text.encode()).decode()
        except Exception as e:
            logging.error(f"Encryption failed: {e}")
            raise Exception(f"Encryption failed: {e}")

    def decrypt(self, ciphertext: str) -> str:
        """Decrypts a string and returns the original text"""
        try:
            return self.cipher.decrypt(ciphertext.encode()).decode()
        except InvalidToken:
            logging.warning("Decryption failed: Invalid token.")
            raise ValueError("Unable to decrypt: Invalid token")
        except Exception as e:
            logging.error(f"Decryption failed: {e}")
            raise Exception(f"Decryption failed: {e}")