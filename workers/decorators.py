from django.shortcuts import redirect

from .utils import szef_exists  # Import our new helper


def szef_check_required(view_func):
    """
    Decorator for views that checks if a user is logged in.
    """

    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if not szef_exists():
                return redirect("register")
            else:
                return redirect("login")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
