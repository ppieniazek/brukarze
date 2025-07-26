from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("test/", views.test, name="test"),
    path("time-stream/", views.time_stream, name="time_stream"),
    # Login views
    path("register/", views.szef_registration, name="register"),
    path(
        "login/",
        views.CustomLoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # Main views
    path("", views.dashboard, name="dashboard"),
    # Szef views
    path("workers/", views.worker_list, name="worker_list"),
    path("workers/search/", views.worker_search, name="worker_search"),
    path("workers/create/", views.worker_create, name="worker_create"),
]
