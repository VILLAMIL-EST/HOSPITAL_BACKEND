from django.contrib import admin
from .models import MedicalSpecialty, Doctor, Appointment, AppointmentHistory

@admin.register(MedicalSpecialty)
class MedicalSpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'license_number', 'office', 'is_available')
    list_filter = ('specialty', 'is_available')
    search_fields = ('user__first_name', 'user__last_name', 'license_number')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'specialty', 'appointment_date', 'appointment_time', 'status')
    list_filter = ('status', 'specialty', 'appointment_date')
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__user__first_name')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'is_locked', 'locked_at')


@admin.register(AppointmentHistory)
class AppointmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'changed_by', 'old_status', 'new_status', 'changed_at')
    list_filter = ('changed_at',)
    readonly_fields = ('appointment', 'changed_by', 'old_status', 'new_status', 'changed_at')