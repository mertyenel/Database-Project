from django.urls import path
from . import views

urlpatterns = [
    path('giris/', views.giris, name='giris'),  # Giriş yap
    path('kayit/', views.kayit, name='kayit'),  # Kayıt ol
    path('home/', views.home, name='home'),  # Ana sayfa
    path('profil/', views.profil, name='profil'),  # Profil
    path('sikayet/', views.sikayet, name='sikayet'),  # Şikayet
    path('durak/', views.durak, name='durak'),  # Durak bilgileri
    path('tramvay/', views.tramvay, name='tramvay'),  # Tramvay bilgileri
    path('forget/', views.forget, name='forget'),
    path('reset/', views.reset, name='reset'),
]