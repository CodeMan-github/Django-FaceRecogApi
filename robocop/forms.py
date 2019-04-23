from django import forms

emailLabel = 'E-mail:'
passwordLabel = 'Password'

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email Address")
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
