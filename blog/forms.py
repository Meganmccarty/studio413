from django import forms
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

from .models import Post, Comment, Subscriber

class PostForm(forms.ModelForm):
    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    text = forms.CharField(widget=SummernoteWidget())
    class Meta:
        model = Post
        fields = ('title', 'text',)

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('name', 'email', 'text',)

class SubscriberForm(forms.Form):
    first_name = forms.CharField(label='Your first name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Your last name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Your email', max_length=100, widget=forms.EmailInput(attrs={'class': 'form-control'}))

class ContactForm(forms.Form):
    name = forms.CharField(label='Your name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Your email', widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(label='Your message', widget=forms.Textarea(attrs={'class': 'form-control'}))