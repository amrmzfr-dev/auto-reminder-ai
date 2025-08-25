# accounts/decorators.py
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def role_required(required_role):
    """
    A centralized decorator to restrict access to views based on the user's role.
    It ensures that only users with a specific 'required_role' can access the view.

    Args:
        required_role (str): The role string ('1' for Admin, '2' for Installer)
                             that is required to access the decorated view.

    Returns:
        function: A decorator that wraps the view function, enforcing role-based access.
    """
    def decorator(view_func):
        @wraps(view_func)  # Preserves the original function's metadata
        @login_required    # Ensures the user is logged in
        def _wrapped_view(request, *args, **kwargs):
            # Check if the logged-in user's role matches the required role
            if hasattr(request.user, 'role') and request.user.role == required_role:
                return view_func(request, *args, **kwargs)
            # If roles do not match, return an HTTP 403 Forbidden response
            return HttpResponseForbidden("❌ Access Denied")
        return _wrapped_view
    return decorator
