from django import forms
from django.contrib.auth import get_user_model
from allauth.account.forms import SignupForm

class CustomSignupForm(SignupForm): 
    first_name = forms.CharField(label='First name', max_length=50, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(label='Last name', max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))

    class Meta:
        fields = ("first_name", "last_name", "email", "username", "password1", "password2")
        model = get_user_model()
    
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': ''
            })

    def signup(self, request, user): 
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user