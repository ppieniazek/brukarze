from django.contrib.auth.forms import UserCreationForm

from .models import User  # Correctly imports from workers.models


class SzefRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)
