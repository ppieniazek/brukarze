import asyncio
from datetime import datetime

from asgiref.sync import sync_to_async
from datastar_py import consts
from datastar_py.django import DatastarResponse, read_signals
from datastar_py.django import ServerSentEventGenerator as SSE
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .decorators import szef_check_required
from .forms import SzefRegistrationForm, WorkerCreateForm, WorkerEditForm
from .models import User, Worker
from .utils import szef_exists


async def test(request):
    return await sync_to_async(render)(request, "workers/test.html")


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


@szef_check_required
def dashboard(request):
    """
    Renders the correct dashboard. The decorator handles unauthenticated users.
    """
    if request.user.groups.filter(name="Szef").exists():
        return render(request, "szef_dashboard.html")
    elif request.user.groups.filter(name="Brygadzista").exists():
        return render(request, "brygadzista_dashboard.html")
    else:
        return redirect("test")


@szef_check_required
def worker_list(request):
    if not request.user.groups.filter(name="Szef").exists():
        return redirect("dashboard")

    workers = Worker.objects.all()
    workers = workers.order_by("is_active", "last_name")
    form = WorkerCreateForm()

    # Pass the search term back to the template
    context = {"workers": workers, "form": form}
    return render(request, "workers/workers.html", context)


@require_GET
async def worker_search(request):
    if "Datastar-Request" not in request.headers:
        return DatastarResponse()
    signals = read_signals(request)
    if signals:
        workers = await sync_to_async(Worker.objects.filter)(
            Q(last_name__icontains=signals["search"])
            | Q(first_name__icontains=signals["search"])
        )
        print(signals["search"])
    else:
        workers = await sync_to_async(Worker.objects.all)()

    table = await sync_to_async(render_to_string)(
        "workers/partials/_worker_table.html", {"workers": workers}
    )

    return DatastarResponse(
        SSE.patch_elements(table, "#worker-table", mode=consts.ElementPatchMode.REPLACE)
    )


@require_POST
def worker_create(request):
    if "Datastar-Request" not in request.headers:
        return DatastarResponse()

    form = WorkerCreateForm(request.POST)

    if form.is_valid():
        form.save()
        # On success, close the modal and reload the table to show the new worker
        workers = Worker.objects.all().order_by("is_active", "last_name")
        worker_table = render_to_string(
            "workers/partials/_worker_table.html", {"workers": workers}
        )
        return DatastarResponse(
            (
                SSE.patch_signals({"worker_modal": False}),
                SSE.patch_elements(worker_table, "#worker-table"),
            )
        )
    else:
        # On failure, re-render the form with errors and patch it into the modal
        form_html = render_to_string(
            "workers/partials/_worker_form.html", {"form": form}, request=request
        )
        return DatastarResponse(SSE.patch_elements(form_html, "#worker-form"))
