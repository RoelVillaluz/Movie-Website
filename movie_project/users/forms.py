from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django import forms
from movies.models import User
from users.models import CustomList


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ListForm(forms.ModelForm):
    class Meta:
        model = CustomList
        
        fields = ["name", "movies"]