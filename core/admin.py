from django.contrib import admin
from django.http import HttpResponse
import json
from .models import (
    Kullanici, GirisLog, Sikayet, Tramvay, Vagon, Durak, DurakTramvay, Kapi, Gecis, Kamera
)

def export_as_json(modeladmin, request, queryset):
    """
    Seçilen queryset'i JSON olarak dışa aktarma fonksiyonu.
    """
    data = list(queryset.values()) 
    response = HttpResponse(
        json.dumps(data, indent=4, ensure_ascii=False), 
        content_type="application/json"
    )
    response['Content-Disposition'] = f'attachment; filename="{modeladmin.model._meta.model_name}_export.json"'
    return response

export_as_json.short_description = "Seçili verileri JSON olarak dışa aktar"

# Kullanıcı modelinin admin görünümü
@admin.register(Kullanici)
class KullaniciAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_filter = ('email',)
    ordering = ('id',)
    actions = [export_as_json]

# Giriş Log modelinin admin görünümü
@admin.register(GirisLog)
class GirisLogAdmin(admin.ModelAdmin):
    list_display = ('giris_id', 'kullanici_id', 'giris_tarihi', 'giris_saati')
    search_fields = ('kullanici_id__first_name', 'kullanici_id__last_name', 'kullanici_id__email')
    list_filter = ('giris_tarihi',)
    ordering = ('-giris_tarihi', '-giris_saati')
    actions = [export_as_json]

# Şikayet modelinin admin görünümü
@admin.register(Sikayet)
class SikayetAdmin(admin.ModelAdmin):
    list_display = ('id', 'kullanici', 'yorum', 'date')
    search_fields = ('kullanici__email', 'yorum')
    list_filter = ('date',)
    ordering = ('-date',)
    actions = [export_as_json]

# Tramvay modelinin admin görünümü
@admin.register(Tramvay)
class TramvayAdmin(admin.ModelAdmin):
    list_display = ('Tramvay_ID', 'Hat_Ismi', 'Vagon_Sayisi', 'Sefer_Baslangic_Saati', 'Sefer_Bitis_Saati', 'Sefer_Yonu')
    search_fields = ('Hat_Ismi', 'Sefer_Yonu')
    list_filter = ('Sefer_Yonu',)
    ordering = ('Tramvay_ID',)
    actions = [export_as_json]

# Vagon modelinin admin görünümü
@admin.register(Vagon)
class VagonAdmin(admin.ModelAdmin):
    list_display = ('Vagon_ID', 'Tramvay', 'Yolcu_Kapasitesi', 'Engelli_Kapasitesi', 'Yolcu_Sayisi', 'Engelli_Sayisi')
    search_fields = ('Tramvay__Hat_Ismi',)
    list_filter = ('Tramvay',)
    ordering = ('Vagon_ID',)
    actions = [export_as_json]

# Durak modelinin admin görünümü
@admin.register(Durak)
class DurakAdmin(admin.ModelAdmin):
    list_display = ('Durak_ID', 'Durak_Adi', 'Kapi_Sayisi')
    search_fields = ('Durak_Adi',)
    ordering = ('Durak_ID',)
    actions = [export_as_json]

# DurakTramvay modelinin admin görünümü
@admin.register(DurakTramvay)
class DurakTramvayAdmin(admin.ModelAdmin):
    list_display = ('id', 'Durak', 'Tramvay', 'Beklenen_Giris_Saati', 'Giris_Saati', 'Cikis_Saati', 'Tarih')
    search_fields = ('Durak__Durak_Adi', 'Tramvay__Hat_Ismi')
    list_filter = ('Tarih',)
    ordering = ('-Tarih',)
    actions = [export_as_json]

# Kapı modelinin admin görünümü
@admin.register(Kapi)
class KapiAdmin(admin.ModelAdmin):
    list_display = ('Kapi_ID', 'Durak', 'Isik_Durumu')
    search_fields = ('Durak__Durak_Adi',)
    list_filter = ('Isik_Durumu',)
    ordering = ('Kapi_ID',)
    actions = [export_as_json]

# Geçiş modelinin admin görünümü
@admin.register(Gecis)
class GecisAdmin(admin.ModelAdmin):
    list_display = ('id', 'Kapi', 'Vagon', 'Toplam_Gecen_Yolcu_Sayisi', 'Toplam_Gecen_Engelli_Sayisi', 'Saat', 'Tarih')
    search_fields = ('Kapi__Durak__Durak_Adi', 'Vagon__Tramvay__Hat_Ismi')
    list_filter = ('Tarih',)
    ordering = ('-Tarih', '-Saat')
    actions = [export_as_json]

# Kamera modelinin admin görünümü
@admin.register(Kamera)
class KameraAdmin(admin.ModelAdmin):
    list_display = ('Kamera_ID', 'Kapi', 'Durum', 'Giren_Yolcu_Sayisi', 'Cikan_Yolcu_Sayisi', 'Giren_Engelli_Sayisi', 'Cikan_Engelli_Sayisi')
    search_fields = ('Kapi__Durak__Durak_Adi', 'Durum')
    list_filter = ('Durum',)
    ordering = ('Kamera_ID',)
    actions = [export_as_json]