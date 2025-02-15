# Generated by Django 5.1 on 2024-09-20 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0051_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendarevent',
            name='location',
            field=models.CharField(choices=[('#212 Jayanagr 2nd block CIMS 2nd floor', '#212 Jayanagr 2nd block CIMS 2nd floor'), ('#414 Majestic opposit to ABC Buliding, 3rd floor', '#414 Majestic opposit to ABC Buliding, 3rd floor'), ('#2 Rajaji Nagar 2nd block XYZ hospital 4th floor', '#2 Rajaji Nagar 2nd block XYZ hospital 4th floor'), ('#78 Banashankri 2nd Stage medical Hospital 1st floor', '#78 Banashankri 2nd Stage medical Hospital 1st floor')], default='Not Selected', max_length=200),
        ),
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='e9cbf4', max_length=6),
        ),
    ]
