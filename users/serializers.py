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

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name',
                  'document_type', 'document_number', 'role', 'phone', 'address', 'birth_date']

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
        # ✅ IMPORTANTE: Eliminar password2 ANTES de crear el usuario
        validated_data.pop('password2')  # ← Esta línea es CRUCIAL
        
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user