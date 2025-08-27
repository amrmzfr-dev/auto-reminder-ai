# views/installer_views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from ..models import InstallerProfile, Installation
from ..forms import InstallerProfileForm
from ..decorators import role_required
from ..services import InstallationService


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

    # Use service layer to get installations and calculate stats
    installations = InstallationService.get_installer_installations(profile)
    stats = InstallationService.calculate_installer_stats(installations)

    context = {
        'profile': profile,
        'installations': installations,
        **stats,  # Unpack all stats into context
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