# Generated by Django 5.1.5 on 2025-01-16 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0052_alter_calendarevent_location_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='8d6915', max_length=6),
        ),
    ]
