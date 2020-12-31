from django.contrib.auth import forms
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError



class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']
    def clean(self):
        super().clean()
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email id already exists",code="invalid")
        return self.cleaned_data


class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password']