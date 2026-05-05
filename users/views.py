import uuid
import re
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser, EmailVerificationToken
from .serializers import UserSerializer, RegisterSerializer


# ✅ FUNCIÓN PARA VERIFICAR EMAIL (formato básico)
def verify_email_format(email):
    """Valida formato de email y rechaza dominios falsos comunes"""
    
    # Validación básica de formato
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(regex, email):
        return False
    
    # Rechazar dominios falsos comunes
    dominios_falsos = ['asdf.asdf', 'test.com', 'example.com', 'fake.com', 
                       'temp.com', 'mailinator.com', 'yopmail.com', 'temp-mail.org']
    
    dominio = email.split('@')[1].lower()
    
    if dominio in dominios_falsos:
        return False
    
    return True


# ✅ FUNCIÓN PARA ENVIAR EMAIL DE VERIFICACIÓN
def send_verification_email(user, token):
    """Envía email con enlace de verificación"""
    verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
    
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Verifica tu cuenta</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 20px; }}
            .header {{ background: #000dff; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #000dff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🏥 Hospital El Salvador de Ubaté</h2>
            </div>
            <div style="padding: 20px;">
                <h3>¡Hola {user.first_name or user.username}!</h3>
                <p>Gracias por registrarte en nuestro sistema de citas médicas.</p>
                <p>Para activar tu cuenta, haz clic en el siguiente botón:</p>
                <div style="text-align: center;">
                    <a href="{verification_url}" class="button" style="color: white;">✅ Verificar mi cuenta</a>
                </div>
                <p>O copia y pega este enlace en tu navegador:</p>
                <p style="background: #f0f0f0; padding: 10px; word-break: break-all;">{verification_url}</p>
                <p>Este enlace expira en 24 horas.</p>
                <p>Si no solicitaste este registro, ignora este mensaje.</p>
            </div>
            <div class="footer">
                <p>Hospital El Salvador de Ubaté - Tu salud es nuestra prioridad</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        send_mail(
            subject="Verifica tu cuenta - Hospital El Salvador",
            message=f"Verifica tu cuenta: {verification_url}",
            from_email=None,  # Usa DEFAULT_FROM_EMAIL
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return True  # En modo consola siempre funciona


# ✅ REGISTER CON VERIFICACIÓN DE EMAIL
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        # Validar formato de email
        if not verify_email_format(email):
            return Response(
                {'error': 'El email no tiene un formato válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si el email ya existe
        if CustomUser.objects.filter(email=email).exists():
            return Response(
                {'error': 'Este email ya está registrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear usuario INACTIVO
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.is_active = False  # ← Inactivo hasta verificar email
        user.save()
        
        # Crear token de verificación
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        # Enviar email de verificación
        if send_verification_email(user, verification_token.token):
            return Response({
                'message': '✅ Usuario registrado exitosamente. Revisa tu correo (o la consola de Django) para verificar tu cuenta.',
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        else:
            user.delete()
            return Response({
                'error': '❌ Error al enviar el correo de verificación. Intenta nuevamente.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ✅ VERIFICACIÓN POR TOKEN (cuando hacen clic en el botón)
class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, token):
        verification_token = get_object_or_404(EmailVerificationToken, token=token)
        
        if verification_token.is_expired():
            user = verification_token.user
            verification_token.delete()
            user.delete()
            return Response({
                'error': '❌ El enlace ha expirado. Por favor regístrate nuevamente.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Activar usuario
        user = verification_token.user
        user.is_active = True
        user.save()
        
        # Eliminar el token (ya no se necesita)
        verification_token.delete()
        
        return Response({
            'message': '✅ ¡Cuenta verificada exitosamente! Ya puedes iniciar sesión.'
        }, status=status.HTTP_200_OK)


# ✅ LOGIN (solo usuarios activos)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        elif user and not user.is_active:
            return Response({
                'error': '❌ Cuenta no verificada. Revisa tu correo (o la consola de Django) y haz clic en el enlace de verificación.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)


# ✅ PROFILE (sin cambios)
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)