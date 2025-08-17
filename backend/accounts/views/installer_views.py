# views/installer_views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from functools import wraps
from ..models import InstallerProfile, Installation
from ..forms import InstallerProfileForm

# -----------------------------------------------
# 🛡️ Role-Based Access Control Decorator
# -----------------------------------------------
def role_required(required_role):
    """
    A custom decorator to restrict access to views based on the user's role.
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


# ------------------------------
# 👷 Installer Dashboard View
# ------------------------------
@role_required('2')
def installer_dashboard_view(request):
    try:
        profile = InstallerProfile.objects.get(user=request.user)
        if profile.registration_status == 'incomplete':
            messages.warning(request, "⚠️ Your registration is incomplete. Please complete your company profile to proceed.")
    except InstallerProfile.DoesNotExist:
        messages.error(request, "Installer profile not found. Please contact support.")
        return redirect('logout')

    # Filter installations for this installer only
    installations = Installation.objects.filter(installer=profile).order_by('-installation_created_date')

    # Your KPI stats code here (optional)
    total_tasks = installations.count()
    in_progress = installations.filter(status='IN_PROGRESS').count()
    pending = installations.filter(status='PENDING_ACCEPTANCE').count()
    completed = installations.filter(status='COMPLETED').count()
    completion_rate = int((completed / total_tasks) * 100) if total_tasks > 0 else 0

    context = {
        'profile': profile,
        'installations': installations,
        'total_tasks': total_tasks,
        'in_progress': in_progress,
        'pending': pending,
        'completion_rate': completion_rate,
    }
    return render(request, 'accounts/installer/installer_dashboard.html', context)

# -----------------------------------------------
# 📋 Installer Profile Detail View (Class-Based)
# -----------------------------------------------
@method_decorator([login_required, role_required('2')], name='dispatch')
class ProfileDetailView(LoginRequiredMixin, DetailView):
    """
    A class-based view to display the details of an installer's profile.
    Requires login and an 'Installer' role.
    """
    model = InstallerProfile
    template_name = 'accounts/installer/profile_detail.html'

    def get_object(self):
        # This method ensures that an installer can only view their own profile.
        # It retrieves the InstallerProfile instance associated with the logged-in user.
        return self.request.user.installerprofile

# -----------------------------------------------
# 📝 Installer Profile Update View (Class-Based)
# -----------------------------------------------
@method_decorator([login_required, role_required('2')], name='dispatch')
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    A class-based view to allow an installer to update their profile.
    Requires login and an 'Installer' role.
    """
    model = InstallerProfile
    form_class = InstallerProfileForm
    template_name = 'accounts/installer/profile_edit.html'
    success_url = reverse_lazy('company_profile') # URL to redirect to on successful update

    def get_object(self):
        # Ensures that an installer can only edit their own profile.
        return self.request.user.installerprofile