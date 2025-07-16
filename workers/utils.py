from django.contrib.auth.models import Group

from .models import User


def szef_exists():
    """Helper function to check if a Szef user exists."""
    try:
        szef_group = Group.objects.get(name="Szef")
        return User.objects.filter(groups=szef_group).exists()
    except Group.DoesNotExist:
        return False
