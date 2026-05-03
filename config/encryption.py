from cryptography.fernet import Fernet
from django.conf import settings
import base64
import logging

logger = logging.getLogger(__name__)

class ClinicalResultEncryption:
    """Cifrado para resultados clínicos (PDFs)"""
    
    @staticmethod
    def _get_cipher():
        """Obtener cipher de Fernet"""
        key = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].encode())
        return Fernet(key)
    
    @staticmethod
    def encrypt_file(file_content: bytes) -> bytes:
        """Cifrar archivo PDF"""
        try:
            cipher = ClinicalResultEncryption._get_cipher()
            return cipher.encrypt(file_content)
        except Exception as e:
            logger.error(f"Error encriptando archivo: {e}")
            raise ValueError("No se pudo encriptar el archivo")
    
    @staticmethod
    def decrypt_file(encrypted_content: bytes) -> bytes:
        """Descifrar archivo PDF"""
        try:
            cipher = ClinicalResultEncryption._get_cipher()
            return cipher.decrypt(encrypted_content)
        except Exception as e:
            logger.error(f"Error desencriptando archivo: {e}")
            raise ValueError("No se pudo desencriptar el archivo")
    
    @staticmethod
    def generate_secure_password() -> str:
        """Generar contraseña segura para un PDF específico"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(12))