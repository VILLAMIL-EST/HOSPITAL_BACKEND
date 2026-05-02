import hashlib
import secrets
import base64
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class DataSecurity:
    """Clase para manejar seguridad de datos sensibles"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hashear contraseñas"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            b'hospital_salt',
            100000
        ).hex()
    
    @staticmethod
    def generate_token() -> str:
        """Generar token seguro"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def _get_cipher():
        """Obtener cipher de Fernet (método interno)"""
        key = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].encode())
        return Fernet(key)
    
    @staticmethod
    def encrypt_data(data: str) -> str:
        """Encriptar datos sensibles"""
        try:
            cipher = DataSecurity._get_cipher()
            return cipher.encrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"Error encriptando datos: {e}")
            raise ValueError("No se pudo encriptar la información")
    
    @staticmethod
    def decrypt_data(encrypted_data: str) -> str:
        """Desencriptar datos sensibles"""
        try:
            cipher = DataSecurity._get_cipher()
            return cipher.decrypt(encrypted_data.encode()).decode()
        except InvalidToken:
            logger.error("Token inválido para desencriptar")
            raise ValueError("La información está corrupta o es inválida")
        except Exception as e:
            logger.error(f"Error desencriptando datos: {e}")
            raise ValueError("No se pudo desencriptar la información")