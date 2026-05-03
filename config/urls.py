from django.contrib import admin
from django.urls import path, include  # ← AGREGAR 'include' aquí

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),  # ← Ahora funciona
]