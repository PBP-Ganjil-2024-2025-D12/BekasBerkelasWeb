from django import forms
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from .models import UserProfile

class UpdateEmailForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        validator = EmailValidator()
        try:
            validator(email)
        except ValidationError:
            raise forms.ValidationError('Invalid Email')
        return email

class UpdatePhoneForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['no_telp']

    def clean_no_telp(self):
        no_telp = self.cleaned_data.get('no_telp')
        if not no_telp.isdigit():
            raise forms.ValidationError('Nomor Telepon hanya menerima digits')
        return no_telp

class UpdateNameForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name']