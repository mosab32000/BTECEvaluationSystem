from cryptography.fernet import Fernet, InvalidToken
import base64
import logging

class Vault:
    def __init__(self, key):
        if not key:
            logging.error("Encryption key is missing!")
            raise ValueError("ENCRYPTION_KEY environment variable not set.")
        try:
            # Use the key directly without additional decoding
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        except (ValueError, TypeError) as e:
            logging.error(f"Invalid encryption key format: {e}")
            raise ValueError("Invalid ENCRYPTION_KEY format. Ensure it's base64 encoded.")

    def encrypt(self, text: str) -> str:
        try:
            return self.cipher.encrypt(text.encode()).decode()
        except Exception as e:
            logging.error(f"Encryption failed: {e}")
            return ""  # Or raise an exception

    def decrypt(self, ciphertext: str) -> str:
        try:
            return self.cipher.decrypt(ciphertext.encode()).decode()
        except InvalidToken:
            logging.warning("Decryption failed: Invalid token.")
            return ""  # Or raise a specific error/None
        except Exception as e:
            logging.error(f"Decryption failed: {e}")
            return ""  # Or raise an exception
