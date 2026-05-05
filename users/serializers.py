import re
from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'document_type', 'document_number', 'role', 'phone', 
                  'address', 'birth_date', 'verification_status']
        read_only_fields = ['verification_status']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    phone = serializers.CharField(required=True)  # ← AGREGAR ESTA LÍNEA (hace obligatorio el teléfono)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name',
                  'document_type', 'document_number', 'role', 'phone', 'address', 'birth_date']

    def validate_phone(self, value):
        """Validación de teléfono: exactamente 10 dígitos, solo números"""
        
        # Si el campo está vacío, es válido (opcional)
        if not value:
            raise serializers.ValidationError("El teléfono es obligatorio")  # ← CAMBIADO
        
        # Limpiar espacios, guiones, paréntesis
        cleaned = re.sub(r'[\s\-\(\)]', '', value)
        
        # Verificar que solo contenga números
        if not cleaned.isdigit():
            raise serializers.ValidationError("El teléfono solo debe contener números")
        
        # Verificar que tenga exactamente 10 dígitos
        if len(cleaned) != 10:
            raise serializers.ValidationError("El teléfono debe tener exactamente 10 dígitos")
        
        return cleaned

    def validate_password(self, value):
        """Validación de contraseña segura"""
        errors = []
        
        if len(value) < 8:
            errors.append("La contraseña debe tener al menos 8 caracteres")
        
        if not re.search(r'[A-Z]', value):
            errors.append("La contraseña debe tener al menos una letra mayúscula (A-Z)")
        
        if not re.search(r'[a-z]', value):
            errors.append("La contraseña debe tener al menos una letra minúscula (a-z)")
        
        if not re.search(r'\d', value):
            errors.append("La contraseña debe tener al menos un número (0-9)")
        
        if ' ' in value:
            errors.append("La contraseña no puede contener espacios")
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user