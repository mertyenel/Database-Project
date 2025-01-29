
from django.db import models

class Kullanici(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Şifre düz metin olarak saklanır
    phone = models.CharField(max_length=11, unique=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class GirisLog(models.Model):
    giris_id = models.AutoField(primary_key=True)
    kullanici_id = models.ForeignKey(Kullanici, on_delete=models.CASCADE, related_name='giris_loglari')
    giris_tarihi = models.DateField(auto_now_add=True)  # Giriş tarihi otomatik atanır
    giris_saati = models.TimeField(auto_now_add=True)  # Giriş saati otomatik atanır

    def __str__(self):
        return f'Giriş ID: {self.giris_id}, Kullanıcı ID: {self.kullanici_id.id}, Tarih: {self.giris_tarihi}'
    
class Sikayet(models.Model):
    kullanici = models.ForeignKey(Kullanici, on_delete=models.CASCADE, related_name='sikayetler')
    yorum = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Sikayet {self.id} by {self.kullanici.email}'
    
class Tramvay(models.Model):
    Tramvay_ID = models.AutoField(primary_key=True)
    Hat_Ismi = models.CharField(max_length=255)
    Vagon_Sayisi = models.IntegerField()
    Sefer_Baslangic_Saati = models.TimeField()
    Sefer_Bitis_Saati = models.TimeField()
    Sefer_Yonu = models.CharField(max_length=255)

    def __str__(self):
        return self.Hat_Ismi


class Vagon(models.Model):
    Vagon_ID = models.AutoField(primary_key=True)
    Tramvay = models.ForeignKey(Tramvay, on_delete=models.CASCADE)
    Yolcu_Kapasitesi = models.IntegerField()
    Engelli_Kapasitesi = models.IntegerField()
    Yolcu_Sayisi = models.IntegerField()
    Engelli_Sayisi = models.IntegerField()
    Yolcu_Yogunlugu = models.CharField(max_length=255)

    def __str__(self):
        return f"Vagon {self.Vagon_ID} - {self.Tramvay.Hat_Ismi}"
    
class Durak(models.Model):
    Durak_ID = models.AutoField(primary_key=True)  # Otomatik artan ID
    Durak_Adi = models.CharField(max_length=255, unique=True)  # Benzersiz durak adı
    Kapi_Sayisi = models.IntegerField()

    def __str__(self):
        return self.Durak_Adi    

class DurakTramvay(models.Model):
    Durak = models.ForeignKey(Durak, on_delete=models.CASCADE)
    Tramvay = models.ForeignKey('Tramvay', on_delete=models.CASCADE)  # Tramvay modeli önceden tanımlı
    Beklenen_Giris_Saati = models.TimeField()
    Giris_Saati = models.TimeField()
    Cikis_Saati = models.TimeField()
    Tarih = models.DateField()

    def __str__(self):
        return f"{self.Durak.Durak_Adi} - {self.Tramvay.Hat_Ismi} ({self.Tarih})"

class Kapi(models.Model):
    Kapi_ID = models.AutoField(primary_key=True)
    Durak = models.ForeignKey(Durak, on_delete=models.CASCADE, related_name="kapilar")
    Isik_Durumu = models.CharField(max_length=255)  # Örneğin: "Açık", "Kapalı"

    def __str__(self):
        return f"{self.Durak.Durak_Adi} - Kapı {self.Kapi_ID}"
    
class Gecis(models.Model):
    Kapi = models.ForeignKey(Kapi, on_delete=models.CASCADE, related_name="gecisler")
    Vagon = models.ForeignKey(Vagon, on_delete=models.CASCADE, related_name="gecisler")
    Toplam_Gecen_Yolcu_Sayisi = models.IntegerField()
    Toplam_Gecen_Engelli_Sayisi = models.IntegerField()
    Saat = models.TimeField()
    Tarih = models.DateField()


    class Meta:
        unique_together = (("Kapi", "Vagon"),)  # Kapı ve Vagon kombinasyonu benzersiz olacak

    def __str__(self):
        return f"Geçiş: Kapı {self.Kapi.Kapi_ID} - Vagon {self.Vagon.Vagon_ID} ({self.Tarih})"
    
class Kamera(models.Model):
    Kamera_ID = models.AutoField(primary_key=True)  # Otomatik artan ID
    Kapi = models.ForeignKey(Kapi, on_delete=models.CASCADE, related_name="kameralar")
    Durum = models.CharField(max_length=255)  # Örneğin: "Aktif", "Bozuk"
    Giren_Yolcu_Sayisi = models.IntegerField()
    Cikan_Yolcu_Sayisi = models.IntegerField()
    Giren_Engelli_Sayisi = models.IntegerField()
    Cikan_Engelli_Sayisi = models.IntegerField()

    def __str__(self):
        return f"Kamera {self.Kamera_ID} - Kapı {self.Kapi.Kapi_ID} ({self.Durum})"