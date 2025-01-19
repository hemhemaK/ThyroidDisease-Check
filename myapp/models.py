import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.conf import settings
import secrets
from django.contrib.auth.models import User
from django.utils import timezone



class Prediction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    age = models.FloatField(default=0.0)
    sex = models.IntegerField(default=0)
    on_thyroxine = models.IntegerField(default=0)
    query_on_thyroxine = models.IntegerField(default=0)
    on_antithyroid_meds = models.IntegerField(default=0)
    sick = models.IntegerField(default=0)
    pregnant = models.IntegerField(default=0)
    thyroid_surgery = models.IntegerField(default=0)
    I131_treatment = models.IntegerField(default=0)
    query_hypothyroid = models.IntegerField(default=0)
    query_hyperthyroid = models.IntegerField(default=0)
    lithium = models.IntegerField(default=0)
    goitre = models.IntegerField(default=0)
    tumor = models.IntegerField(default=0)
    hypopituitary = models.IntegerField(default=0)
    psych = models.IntegerField(default=0)
    TSH_measured = models.IntegerField(default=0)
    TSH = models.FloatField(default=0.0)
    T3_measured = models.IntegerField(default=0)
    T3 = models.FloatField(default=0.0)
    TT4_measured = models.IntegerField(default=0)
    TT4 = models.FloatField(default=0.0)
    T4U_measured = models.IntegerField(default=0)
    T4U = models.FloatField(default=0.0)
    FTI_measured = models.IntegerField(default=0)
    FTI = models.FloatField(default=0.0)
    TBG_measured = models.IntegerField(default=0)
    TBG = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
    result = models.CharField(max_length=100,default='Unknown')  # To store the prediction result

    def __str__(self):
        return f"Prediction by {self.user.username} on {self.created_at}"


# Create your models here.
class MyModel(models.Model):
    name = models.CharField(max_length=100)


class CustomUser(AbstractUser):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = ("email")
    REQUIRED_FIELDS = ["username"]

    def _str__(self):
        return self.email


class OtpToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    otp_code = models.CharField(max_length=6, default=secrets.token_hex(3))
    tp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class CalendarEvent(models.Model):
    LOCATION_CHOICES = [
        ('#212 Jayanagr 2nd block CIMS 2nd floor','#212 Jayanagr 2nd block CIMS 2nd floor'),
        ('#414 Majestic opposit to ABC Buliding, 3rd floor','#414 Majestic opposit to ABC Buliding, 3rd floor'),
        ('#2 Rajaji Nagar 2nd block XYZ hospital 4th floor','#2 Rajaji Nagar 2nd block XYZ hospital 4th floor'),
        ('#78 Banashankri 2nd Stage medical Hospital 1st floor','#78 Banashankri 2nd Stage medical Hospital 1st floor')
    ]

    ROOM_CHOICES = [
        ('Room 1', 'Room 1'),
        ('Room 2', 'Room 2'),
        ('Room 3', 'Room 3'),
        ('Room 4', 'Room 4'),
        ('Room 5', 'Room 5'),

    ]

    DOCTOR_CHOICES = [
        ('Dr. Sanjay', 'Dr. Sanjay'),
        ('Dr. Raji', 'Dr. Raji'),
        ('Dr. Suhas', 'Dr. Suhas'),
        ('Dr. Sachin', 'Dr. Sachin'),
        ('Dr. Divya', 'Dr. Divya'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=200, choices=LOCATION_CHOICES, default='Not Selected')
    room = models.CharField(max_length=200, choices=ROOM_CHOICES, default='Not Selected')
    doctor = models.CharField(max_length=200, choices=DOCTOR_CHOICES, default='Not Selected')

    def __str__(self):
        return self.title


class Enquiry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # Temporarily allow nulls
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    issue = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    replied = models.BooleanField(default=False)
    reply_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.subject}'


class Reply(models.Model):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE)
    reply_message = models.TextField()
    replied_at = models.DateTimeField(auto_now_add=True)


class Event(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    start = models.DateTimeField()
    end = models.DateTimeField()
    deleted = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='deleted_events', on_delete=models.SET_NULL,
                                   null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
