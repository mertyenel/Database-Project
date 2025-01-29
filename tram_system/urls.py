from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),          # Admin paneline erişim
    path('', lambda request: redirect('giris')),  # Varsayılan URL, 'home' sayfasına yönlendirilir
    path('accounts/', include('allauth.urls')),  # Allauth URL'leri
    path('', include('core.urls')),           # 'core' uygulamasının URL'lerini bağlama
]
