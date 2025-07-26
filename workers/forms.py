from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, Worker


class SzefRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)


class WorkerCreateForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["first_name", "last_name", "hourly_wage"]


class WorkerEditForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["first_name", "last_name", "hourly_wage", "is_active"]
