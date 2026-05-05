from django.urls import path
from .views import RegisterView, LoginView, ProfileView, VerifyEmailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('verify/<uuid:token>/', VerifyEmailView.as_view(), name='verify-email'),
]