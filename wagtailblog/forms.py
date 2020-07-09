from django import forms
from django.contrib.auth import get_user_model
from .models import Subscriber

class SubscriberForm(forms.Form):
    first_name = forms.CharField(label='Your first name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Your last name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Your email', max_length=100, widget=forms.EmailInput(attrs={'class': 'form-control'}))

class ContactForm(forms.Form):
    name = forms.CharField(label='Your name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Your email', widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(label='Your message', widget=forms.Textarea(attrs={'class': 'form-control'}))

class CustomSignupForm(forms.Form): 
    first_name = forms.CharField(label='First name', max_length=50, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(label='Last name', max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))

    class Meta:
        fields = ("first_name", "last_name", "email", "username", "password1", "password2")
        model = get_user_model()

    def signup(self, request, user): 
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user