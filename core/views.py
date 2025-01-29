from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection  # Veritabanı bağlantısı için
from .models import Kullanici, Sikayet, Tramvay,Vagon,Kapi,GirisLog,DurakTramvay
from django.utils.timezone import now  # Tarih ve saat için
from django.contrib.auth.hashers import make_password
import random
from django.core.mail import send_mail
from django.conf import settings


def giris(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Formdan e-posta alınır
        password = request.POST.get('password')  # Formdan şifre alınır

        try:
            # Kullanıcıyı veritabanında sorgula
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM core_kullanici WHERE email = %s AND password = %s", [email, password])
                user = cursor.fetchone()  # İlk eşleşen kaydı al

            if user:
                # Eğer kullanıcı bulunduysa
                request.session['authenticated'] = True
                request.session['user_id'] = user[0]  # Veritabanındaki kullanıcı ID

                # Giriş logunu oluştur
                kullanici = Kullanici.objects.get(id=user[0])  # Kullanıcıyı getir
                GirisLog.objects.create(
                    kullanici_id=kullanici,
                    giris_tarihi=now().date(),  # Otomatik tarih
                    giris_saati=now().time()    # Otomatik saat
                )

                return redirect('home')  # Doğru girişte home.html'e yönlendir
            else:
                # Kullanıcı bulunamadıysa
                messages.error(request, "E-posta veya şifre hatalı.")
                return render(request, 'core/giris.html')  # Giriş sayfasında kal

        except Exception as e:
            # Veritabanı hatası durumunda
            messages.error(request, f"Bir hata oluştu: {e}")
            return render(request, 'core/giris.html')  # Giriş sayfasında kal

    # GET isteği için giriş sayfasını döndür
    return render(request, 'core/giris.html')
def forget(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = Kullanici.objects.get(email=email)
            verification_code = random.randint(100000, 999999)
            request.session['verification_code'] = verification_code
            request.session['email'] = email

            send_mail(
                'Şifre Sıfırlama Doğrulama Kodu',
                f'Sayın {user.first_name}, şifre sıfırlama kodunuz: {verification_code}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Doğrulama kodu e-posta adresinize gönderildi.', extra_tags='forget')
            return redirect('reset')
        except Kullanici.DoesNotExist:
            messages.error(request, 'Bu e-posta adresiyle kayıtlı bir kullanıcı bulunamadı.', extra_tags='forget')
    return render(request, 'core/forget.html')

def reset(request):
    if request.method == 'POST':
        entered_code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if int(entered_code) != request.session.get('verification_code'):
            messages.error(request, 'Doğrulama kodu yanlış.', extra_tags='reset')
            return redirect('reset')

        if new_password != confirm_password:
            messages.error(request, 'Şifreler eşleşmiyor.', extra_tags='reset')
            return redirect('reset')

        try:
            email = request.session.get('email')
            user = Kullanici.objects.get(email=email)
            user.password = new_password  
            user.save()
            messages.success(request, 'Şifreniz başarıyla güncellendi. Giriş yapabilirsiniz.', extra_tags='reset')
            return redirect('giris')
        except Kullanici.DoesNotExist:
            messages.error(request, 'Bir hata oluştu. Lütfen tekrar deneyin.', extra_tags='reset')
    return render(request, 'core/reset.html')

def kayit(request):
    if request.method == 'POST':
        # Formdan gelen verileri al
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')

        # Hataları toplamak için bir liste
        errors = []

        # Form doğrulama
        if not first_name.isalpha():
            errors.append("Ad kısmı sadece harf içermelidir.")
        if not last_name.isalpha():
            errors.append("Soyad kısmı sadece harf içermelidir.")
        if len(phone) != 11 or not phone.isdigit():
            errors.append("Telefon numarası 11 haneli olmalı ve sadece rakam içermelidir.")
        if Kullanici.objects.filter(email=email).exists():
            errors.append("Bu email adresi zaten kayıtlı.")
        if Kullanici.objects.filter(phone=phone).exists():
            errors.append("Bu telefon numarası zaten kayıtlı.")

        # Eğer hata varsa formu tekrar göster
        if errors:
            return render(request, 'core/kayit.html', {'errors': errors})

        # Kullanıcıyı veritabanına kaydet
        try:
            yeni_kullanici = Kullanici.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,  # Şifre düz metin olarak saklanıyor
                phone=phone
            )
            yeni_kullanici.save()
            messages.success(request, "Kayıt başarıyla tamamlandı! Giriş yapabilirsiniz.")
            return redirect('giris')  # Giriş sayfasına yönlendirme
        except Exception as e:
            errors.append(f"Bir hata oluştu: {str(e)}")
            return render(request, 'core/kayit.html', {'errors': errors})

    # GET isteğinde formu göster
    return render(request, 'core/kayit.html')
def home(request):
    return render(request, 'core/home.html')


def profil(request):
    if not request.session.get('authenticated', False):
        return redirect('giris')  # Kullanıcı giriş yapmadıysa giris sayfasına yönlendir.

    user_id = request.session.get('user_id')
    try:
        user = Kullanici.objects.get(id=user_id)
    except Kullanici.DoesNotExist:
        return redirect('giris')

    success_message = None  # Başarı mesajı için değişken
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        phone = request.POST.get('phone', '').strip()

        errors = []
        # Validasyon Kontrolleri
        if not all(char.isalpha() or char.isspace() for char in first_name):
            errors.append("Ad kısmı sadece harf ve boşluk içerebilir.")
        if not all(char.isalpha() or char.isspace() for char in last_name):
            errors.append("Soyad kısmı sadece harf ve boşluk içerebilir.")
        if not phone.isdigit() or len(phone) != 11:
            errors.append("Telefon numarası 11 haneli olmalı ve sadece rakam içermelidir.")
        if not email or "@" not in email or "." not in email:
            errors.append("Geçerli bir email adresi giriniz.")
        if Kullanici.objects.filter(email=email).exclude(id=user.id).exists():
            errors.append("Bu email adresi başka bir kullanıcı tarafından kullanılıyor.")
        if Kullanici.objects.filter(phone=phone).exclude(id=user.id).exists():
            errors.append("Bu telefon numarası başka bir kullanıcı tarafından kullanılıyor.")

        if errors:
            # Hatalar varsa formu hatalarla birlikte geri dönder
            return render(request, 'core/profil.html', {
                'errors': errors,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone
            })

        # Kullanıcı bilgilerini güncelle
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone = phone
        if password:
            user.password = password
        user.save()  # Değişiklikleri kaydet

        # Başarı mesajı
        success_message = "Profil başarıyla güncellendi!"

    # GET isteğinde veya POST sonrasında formu mevcut kullanıcı bilgileriyle doldur
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone': user.phone,
        'success_message': success_message  # Başarı mesajını şablona gönder
    }

    return render(request, 'core/profil.html', context)

def sikayet(request):
    if not request.session.get('authenticated', False):
        return redirect('giris')  # Giriş yapmamışsa 'giris' sayfasına yönlendir

    user_id = request.session.get('user_id')
    try:
        user = Kullanici.objects.get(id=user_id)
    except Kullanici.DoesNotExist:
        return redirect('giris')  # Kullanıcı bulunamazsa 'giris' sayfasına yönlendir

    if request.method == 'POST':
        yorum = request.POST.get('yorum', '').strip()

        errors = []
        if not yorum:
            errors.append("Yorum boş bırakılamaz.")
        elif len(yorum) < 10:
            errors.append("Yorum en az 10 karakter olmalıdır.")

        if errors:
            # Hatalar varsa formu hatalarla birlikte geri dönder
            return render(request, 'core/sikayet.html', {
                'errors': errors,
                'yorum': yorum
            })

        # Şikayeti kaydet
        Sikayet.objects.create(kullanici=user, yorum=yorum)

        # Başarı mesajı göstermek için
        return render(request, 'core/sikayet.html', {
            'success': "Şikayetiniz başarıyla gönderildi.",
        })

    return render(request, 'core/sikayet.html')

def durak(request):
    # Eğer 'durak_id' parametresi yoksa, durak.html sayfasını göster
    if request.method == 'GET' and 'durak_id' not in request.GET:
        return render(request, 'core/durak.html')
    
    # Eğer 'durak_id' parametresi varsa, ilgili durağın kapı bilgilerini ve tramvay bilgilerini JSON olarak döndür
    if request.method == 'GET' and 'durak_id' in request.GET:
        durak_id = request.GET.get('durak_id')
        kapilar = Kapi.objects.filter(Durak_id=durak_id).select_related('Durak')

        # core_duraktramvay tablosuna karşılık gelen DurakTramvay modelinden
        # ilgili durak için Beklenen_Giris_Saati en büyük olan kaydı al
        durak_tramvay_kaydi = DurakTramvay.objects.filter(Durak_id=durak_id).order_by('-Beklenen_Giris_Saati').first()

        # Varsayılan değerler
        hatIsmi = "--"
        beklenenGirisSaati = "--"
        tarih = "--"

        # Eğer bir kayıt bulunduysa verileri güncelle
        if durak_tramvay_kaydi is not None:
            hatIsmi = durak_tramvay_kaydi.Tramvay.Hat_Ismi
            beklenenGirisSaati = durak_tramvay_kaydi.Beklenen_Giris_Saati.strftime("%H:%M:%S")
            tarih = durak_tramvay_kaydi.Tarih.strftime("%Y-%m-%d")

        # Kapıları listeleyip JSON olarak döndürelim
        data = []
        for kapi in kapilar:
            data.append({
                "Kapi_ID": kapi.Kapi_ID,
                "Durak_Adi": kapi.Durak.Durak_Adi,
                "Isik_Durumu": kapi.Isik_Durumu,
                "Hat_Ismi": hatIsmi,
                "Beklenen_Giris_Saati": beklenenGirisSaati,
                "Tarih": tarih
            })
        return JsonResponse(data, safe=False)

    # Yukarıdaki koşullar sağlanmazsa geçersiz istek hatası döndür
    return JsonResponse({"error": "Geçersiz istek."}, status=400)

def tramvay(request):
    # Eğer parametre yoksa HTML döndür
    if request.method == 'GET' and 'tram_id' not in request.GET and 'vagon_tram_id' not in request.GET:
        return render(request, 'core/tramvay.html') 

    if request.method == 'GET' and 'tram_id' in request.GET:
        # Tramvay bilgilerini çek
        tram_id = request.GET.get('tram_id')
        try:
            tram = Tramvay.objects.get(Tramvay_ID=tram_id)  
            return JsonResponse({
                "Hat_Ismi": tram.Hat_Ismi,
                "Sefer_Baslangic_Saati": str(tram.Sefer_Baslangic_Saati),
                "Sefer_Bitis_Saati": str(tram.Sefer_Bitis_Saati),
                "Sefer_Yonu": tram.Sefer_Yonu,
            })
        except Tramvay.DoesNotExist:
            return JsonResponse({"error": "Tramvay bulunamadı."}, status=404)

    if request.method == 'GET' and 'vagon_tram_id' in request.GET:
        # Vagon bilgilerini çek
        tram_id = request.GET.get('vagon_tram_id')
        vagons = Vagon.objects.filter(Tramvay_id=tram_id)
        data = []
        for vagon in vagons:
            data.append({
                "Vagon_ID": vagon.Vagon_ID,
                "Yolcu_Kapasitesi": vagon.Yolcu_Kapasitesi,
                "Engelli_Kapasitesi": vagon.Engelli_Kapasitesi,
                "Yolcu_Sayisi": vagon.Yolcu_Sayisi,
                "Engelli_Sayisi": vagon.Engelli_Sayisi,
                "Yolcu_Yogunlugu": vagon.Yolcu_Yogunlugu,
            })
        return JsonResponse(data, safe=False)

    return JsonResponse({"error": "Geçersiz istek."}, status=400)