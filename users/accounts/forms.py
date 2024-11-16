from django import forms
from django.contrib.auth.models import User
from .models import Profile

class RegistrationForm(forms.Form):
    username = forms.CharField(required=True, max_length=100, label='Username')
    email = forms.EmailField(required=True, label='Email')
    password = forms.CharField(required=True, label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(required=True, label='Confirm Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Passwords do not match')
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        return user

    
class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=100,label = "username")
    password = forms.CharField(widget=forms.PasswordInput,required=True,label = 'Password')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'location']

class UsernameChangeForm(forms.Form):
    new_username = forms.CharField(max_length=150, label='New Username')

    def clean_new_username(self):
        username = self.cleaned_data['new_username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username