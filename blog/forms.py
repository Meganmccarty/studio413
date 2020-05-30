from django import forms
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

from .models import Post, Comment, Subscriber

class PostForm(forms.ModelForm):
    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    youtube_video = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}),
                    help_text='This is for a single YouTube video to be displayed at the top of a post. '\
                    'To get the code, go to the video on YouTube, click on the "Share" option, and then '\
                    'click on "Embed". Copy and paste the code here. If you want the video to look good '\
                    'on phones, change the number in quotes for "width" from "560" to "75%" (It is at '\
                    'the very beginning of the code you posted).')
    text = forms.CharField(widget=SummernoteWidget())
    class Meta:
        model = Post
        fields = ('title', 'youtube_video', 'text')

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