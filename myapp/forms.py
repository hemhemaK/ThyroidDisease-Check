from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import CalendarEvent, Enquiry, Event


class RegisterForm(UserCreationForm):
    email = forms.CharField(
        widget=forms.EmailInput(attrs={"placeholder": "Enter email-address", "class": "form-control"}))
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Enter email-username", "class": "form-control"}))
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(
        attrs={"placeholder": "Enter password", "class": "form-control"}))
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(
        attrs={"placeholder": "Confirm password", "class": "form-control"}))

    class Meta:
        model = get_user_model()
        fields = ["email", "username", "password1", "password2"]


class CalendarEventForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ['title', 'description', 'start_time', 'end_time', 'location', 'username', 'room', 'doctor']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class EnquiryForm(forms.ModelForm):
    ISSUE_CHOICES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('feedback', 'General Feedback'),
        ('support', 'Support Request'),
    ]

    # Use ChoiceField for the issue field
    issue = forms.ChoiceField(choices=ISSUE_CHOICES, label="Select Issue",
                              widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Enquiry
        fields = [ 'subject', 'issue', 'message']  # Add 'issue' field
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'issue': forms.Select(choices=[('bug', 'Bug Report'), ('feature', 'Feature Request'), ('feedback', 'General Feedback'), ('support', 'Support Request')], attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message'}),
        }




