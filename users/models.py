from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """Modelo de usuario personalizado para el Hospital El Salvador de Ubaté"""
    
    # Roles de usuario (según documento)
    ROLES = (
        ('paciente', 'Paciente'),
        ('medico', 'Médico'),
        ('administrativo', 'Administrativo'),
    )
    
    # Tipos de documento de identidad
    DOCUMENT_TYPES = (
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
        ('RC', 'Registro Civil'),
        ('PA', 'Pasaporte'),
    )
    
    # Estados de verificación 
    VERIFICATION_STATUS = (
        ('pending', 'Pendiente de verificación'),
        ('verified', 'Verificado - Paciente del hospital'),
        ('rejected', 'Rechazado - No pertenece al hospital'),
        ('external', 'Externo - Solo consulta de resultados'),
    )
    
    # Datos personales
    document_type = models.CharField(max_length=2, choices=DOCUMENT_TYPES, default='CC')
    document_number = models.CharField(max_length=20, unique=True, verbose_name='Número de documento')
    role = models.CharField(max_length=20, choices=ROLES, default='paciente')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    address = models.TextField(blank=True, verbose_name='Dirección')
    birth_date = models.DateField(null=True, blank=True)
    
    # Estado de verificación (para integrar con HIS del hospital)
    verification_status = models.CharField(
        max_length=20, 
        choices=VERIFICATION_STATUS, 
        default='pending',
        verbose_name='Estado de verificación'
    )
    verified_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_users',  # ← CORREGIDO
        verbose_name='Verificado por'
    )
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de verificación')
    verification_notes = models.TextField(blank=True, verbose_name='Notas de verificación')
    
    # Para tutores (gestión de menores) - según documento página 21
    is_tutor = models.BooleanField(default=False, verbose_name='Es tutor legal')
    tutored_patients = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        blank=True,
        related_name='tutors',  # ← CORREGIDO
        verbose_name='Pacientes a cargo'
    )
    
    # Para pacientes externos (Convida, Cafam, etc.)
    external_eps = models.CharField(max_length=100, blank=True, verbose_name='EPS externa')
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.document_number}"
    
    def can_book_appointment(self):
        """Verifica si el usuario puede agendar citas"""
        return self.verification_status == 'verified'
    
    def can_view_results(self):
        """Verifica si el usuario puede ver resultados"""
        return self.verification_status in ['verified', 'external']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'