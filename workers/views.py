import asyncio
from datetime import datetime

from datastar_py.django import DatastarResponse
from datastar_py.django import ServerSentEventGenerator as SSE
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .decorators import szef_check_required
from .forms import SzefRegistrationForm
from .models import User
from .utils import szef_exists


def test(request):
    return render(request, "workers/test.html")


async def time_stream(request):
    async def event_stream():
        while True:
            now = datetime.now().strftime("%H:%M:%S")
            yield SSE.patch_signals({"currentTime": now})
            await asyncio.sleep(1)

    return DatastarResponse((event_stream()))


class CustomLoginView(LoginView):
    """
    Custom login view that redirects to registration if no Szef exists.
    """

    def dispatch(self, request, *args, **kwargs):
        if not szef_exists():
            return redirect("register")
        return super().dispatch(request, *args, **kwargs)


@szef_check_required
def dashboard(request):
    """
    Renders the correct dashboard. The decorator handles unauthenticated users.
    """
    if request.user.groups.filter(name="Szef").exists():
        return render(request, "workers/szef_dashboard.html")
    elif request.user.groups.filter(name="Brygadzista").exists():
        return render(request, "workers/brygadzista_dashboard.html")
    else:
        return redirect("test")


def szef_registration(request):
    """Handles registration for the 'Szef' user, only if one does not exist."""
    # Ensure groups are created before checking
    szef_group, _ = Group.objects.get_or_create(name="Szef")
    Group.objects.get_or_create(name="Brygadzista")

    szef_exists = User.objects.filter(groups=szef_group).exists()

    if szef_exists and not request.user.groups.filter(name="Szef").exists():
        return render(request, "registration/szef_registration_closed.html")

    if request.method == "POST":
        form = SzefRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.groups.add(szef_group)
            login(request, user)
            return redirect("dashboard")
    else:
        form = SzefRegistrationForm()

    return render(request, "registration/szef_registration.html", {"form": form})
