# Generated by Django 5.1 on 2024-09-04 07:48

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0010_remove_prediction_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prediction',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='3e5123', max_length=6),
        ),
    ]
