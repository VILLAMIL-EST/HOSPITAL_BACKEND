from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date, time

class MedicalSpecialty(models.Model):
    """Especialidades médicas"""
    name = models.CharField(max_length=100, verbose_name='Nombre de la especialidad')
    description = models.TextField(blank=True, verbose_name='Descripción')
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Especialidad Médica'
        verbose_name_plural = 'Especialidades Médicas'
        ordering = ['name']


class Doctor(models.Model):
    """Información adicional del médico"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'medico'},
        verbose_name='Usuario'
    )
    specialty = models.ForeignKey(
        MedicalSpecialty, 
        on_delete=models.CASCADE,
        verbose_name='Especialidad'
    )
    license_number = models.CharField(max_length=50, unique=True, verbose_name='Número de licencia')
    office = models.CharField(max_length=10, verbose_name='Consultorio')
    is_available = models.BooleanField(default=True, verbose_name='Disponible')
    consultation_duration = models.IntegerField(default=30, verbose_name='Duración consulta (minutos)')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialty.name}"
    
    class Meta:
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'


class Appointment(models.Model):
    """Citas médicas"""
    
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Completada'),
        ('no_show', 'No asistió'),
    )
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='appointments',
        limit_choices_to={'role': 'paciente'},
        verbose_name='Paciente'
    )
    doctor = models.ForeignKey(
        Doctor, 
        on_delete=models.CASCADE,
        verbose_name='Médico'
    )
    specialty = models.ForeignKey(
        MedicalSpecialty, 
        on_delete=models.CASCADE,
        verbose_name='Especialidad'
    )
    
    appointment_date = models.DateField(verbose_name='Fecha de la cita')
    appointment_time = models.TimeField(verbose_name='Hora de la cita')
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='Estado'
    )
    
    reason = models.TextField(blank=True, verbose_name='Motivo de consulta')
    notes = models.TextField(blank=True, verbose_name='Notas médicas')
    cancellation_reason = models.TextField(blank=True, verbose_name='Razón de cancelación')
    
    # Lease Pattern (bloqueo temporal para evitar doble reserva)
    is_locked = models.BooleanField(default=False, verbose_name='Bloqueada')
    locked_at = models.DateTimeField(null=True, blank=True, verbose_name='Bloqueada desde')
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locked_appointments',
        verbose_name='Bloqueada por'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.specialty.name} - {self.appointment_date} {self.appointment_time}"
    
    def clean(self):
        """Validaciones antes de guardar"""
        # Validar que la fecha no sea pasada
        if self.appointment_date < date.today():
            raise ValidationError('No se pueden agendar citas en fechas pasadas')
        
        # Validar horario laboral (8:00 - 18:00)
        if self.appointment_time < time(8, 0) or self.appointment_time > time(18, 0):
            raise ValidationError('Las citas solo están disponibles de 8:00 a 18:00')
    
    class Meta:
        verbose_name = 'Cita Médica'
        verbose_name_plural = 'Citas Médicas'
        ordering = ['appointment_date', 'appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']


class AppointmentHistory(models.Model):
    """Historial de cambios en citas médico"""
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.appointment} - {self.old_status} → {self.new_status}"
    
    class Meta:
        verbose_name = 'Historial de Cita'
        verbose_name_plural = 'Historial de Citas'
        ordering = ['-changed_at']