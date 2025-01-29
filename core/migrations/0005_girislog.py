# Generated by Django 5.0.6 on 2024-12-16 21:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_durak_tramvay_kapi_kamera_duraktramvay_vagon_gecis'),
    ]

    operations = [
        migrations.CreateModel(
            name='GirisLog',
            fields=[
                ('giris_id', models.AutoField(primary_key=True, serialize=False)),
                ('giris_tarihi', models.DateField(auto_now_add=True)),
                ('giris_saati', models.TimeField(auto_now_add=True)),
                ('kullanici_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='giris_loglari', to='core.kullanici')),
            ],
        ),
    ]
