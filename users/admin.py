from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'document_number', 'role', 'verification_status', 'is_active')
    list_filter = ('role', 'verification_status', 'is_active')
    search_fields = ('username', 'email', 'document_number', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información personal', {
            'fields': ('document_type', 'document_number', 'phone', 'address', 'birth_date')
        }),
        ('Verificación', {
            'fields': ('verification_status', 'verified_by', 'verified_at', 'verification_notes', 'external_eps')
        }),
        ('Roles y permisos', {
            'fields': ('role', 'is_tutor', 'tutored_patients')
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)