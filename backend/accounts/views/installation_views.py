from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden # Keep if needed for custom Forbidden responses in role_required
# from functools import wraps # No longer needed here if role_required handles its own wraps
# from django.contrib.auth.decorators import login_required # No longer needed here if role_required includes it

# IMPORT YOUR EXISTING role_required DECORATOR HERE
# Example: If role_required is in 'my_project/core_app/decorators.py'
# from core_app.decorators import role_required
# Example: If role_required is in 'my_project/accounts/utils.py'
# from accounts.utils import role_required
#
# Placeholder for your import path:
from accounts.views.admin_views import role_required # <<< REPLACE 'your_app_name.decorators' with actual path

from ..forms import InstallationForm
from ..models import ChargerModel # Keep ChargerModel as it's used in Installation model

User = get_user_model()

# The role_required decorator is now imported from another file
# so its definition is removed from here.

@role_required('1')  # Apply the custom role_required decorator for role_id '1'
def create_installation_view(request):
    """
    Handles the creation of a new Installation and its associated Customer.
    Only accessible by users with role '1' (e.g., admin).
    """
    if request.method == 'POST':
        form = InstallationForm(request.POST)
        if form.is_valid():
            print("[DEBUG] Form is valid")
            try:
                form.save()
                print("[DEBUG] Form saved successfully")
                form = InstallationForm()  # Reset form if needed
            except Exception as e:
                form.add_error(None, f"An error occurred during saving: {e}")
                print(f"[ERROR] Saving error: {e}")
        else:
            print(f"[ERROR] Form errors: {form.errors}")
    else:
        form = InstallationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/admin/admin_installation_page.html', context)

@role_required('1')  # Only allow role_id '1' (admin)
def installation_page_view(request):
    """
    Renders the admin installation registration page with an empty form.
    GET only.
    """
    form = InstallationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/admin/admin_installation_page.html', context)