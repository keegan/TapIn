from django import forms

class AuthForm(forms.Form):
    username = forms.CharField(label='username', max_length=12)
    password = forms.CharField(label='password', max_length=100, type="password")
    newPIN = forms.CharField(label='newPin', max_length=6, type="numbers")
    confPIN = forms.CharField(label='confPin', max_length=6, type="numbers")


# Create your views here.
