from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name="has_group")
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
        return group in user.groups.all()
    except Group.DoesNotExist:
        return False


@register.filter(name="is_szef")
def is_szef(user):
    return has_group(user, "Szef")


@register.filter(name="is_brygadzista")
def is_brygadzista(user):
    return has_group(user, "Brygadzista")
