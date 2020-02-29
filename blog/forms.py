from django import forms
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

from .models import Post, Comment

class PostForm(forms.ModelForm):
    text = forms.CharField(widget=SummernoteWidget())
    class Meta:
        model = Post
        fields = ('title', 'text',)

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('name', 'email', 'text',)