from hashlib import pbkdf2_hmac
from cryptography.fernet import Fernet
import base64
import hashlib
import os

def hash_password(password: str) -> str:
    # Используем PBKDF2 вместо SHA-256
    salt = os.urandom(16)
    key = pbkdf2_hmac(
        'sha512',
        password.encode(),
        salt,
        100000,
        dklen=64
    )
    return salt.hex() + key.hex()

class CryptoManager:
    def __init__(self, master_password: str):
        self.master_password = master_password
        self.salt = self.load_or_create_salt()
        self.key = self.derive_key()
        self.cipher = Fernet(self.key)

    def load_or_create_salt(self):
        """Загрузка или генерация соли"""
        salt_file = "salt.key"
        if os.path.exists(salt_file):
            with open(salt_file, "rb") as f:
                return f.read()
        else:
            salt = os.urandom(16)
            with open(salt_file, "wb") as f:
                f.write(salt)
            return salt

    def generate_hmac_key(self):
        return pbkdf2_hmac('sha256', self.master_password.encode(), self.salt, 100000)
    
    def derive_key(self):
        # Генерируем ключ и кодируем в base64
        key_bytes = pbkdf2_hmac(
            'sha512',
            self.master_password.encode(),
            self.salt,
            100000,
            dklen=32  # Явно указываем длину 32 байта
        )
        return base64.urlsafe_b64encode(key_bytes)  # Кодировка для Fernet

    def encrypt(self, data):
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data.encode()).decode()