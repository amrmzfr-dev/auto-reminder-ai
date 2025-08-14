# accounts/views/installation_views.py (or your preferred location)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required # Keep if role_required doesn't include it
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.utils import timezone
import datetime
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
# --- IMPORTANT IMPORTS ---
# Make sure these imports match the actual location of your models
from ..models import CustomUser # Your custom user model
# Assuming these are in 'your_app' (or wherever your Customer, ChargerModel, InstallerProfile are)
from ..models import Customer, ChargerModel, InstallerProfile
from ..models import Installation # Your Installation model
from ..models import Notification # Your Notification model
from django.db import models # Needed for Q objects in installation_list

# Import your InstallationForm
from ..forms import InstallationForm # Adjust this import path if your form is elsewhere
# Import your role_required decorator
from accounts.views.admin_views import role_required # Adjust this import path if decorator is elsewhere

# User = get_user_model() # Typically not needed if CustomUser is directly imported
# --- END IMPORTANT IMPORTS ---


@login_required # Apply login_required here, assuming role_required does not
def installation_list(request):
    """
    Displays a list of installation jobs based on the logged-in user's role.
    Admins see all installations. Installers see only their assigned installations.
    """
    if request.user.role == '1':  # Assuming '1' is the role code for Admin
        installations_queryset = Installation.objects.all().order_by('-created_at')
        page_title = "Admin Dashboard - All Installations"
    elif request.user.role == '2':  # Assuming '2' is the role code for Installer
        # For installers, filter installations where they are directly assigned (CustomUser)
        # OR where their InstallerProfile is assigned
        try:
            installer_profile = InstallerProfile.objects.get(user=request.user)
            installations_queryset = Installation.objects.filter(
                models.Q(assigned_installer=request.user) |
                models.Q(installer=installer_profile)
            ).order_by('-created_at')
            page_title = f"Installer Dashboard - {installer_profile.company_name} Installations"
        except InstallerProfile.DoesNotExist:
            # Handle case where an installer user doesn't have an InstallerProfile yet
            # In this scenario, they can only see jobs directly assigned to their CustomUser account
            installations_queryset = Installation.objects.filter(assigned_installer=request.user).order_by('-created_at')
            page_title = "Installer Dashboard - Your Installations (Profile Missing)"

    else:
        # For any other role or unassigned users, deny access
        return HttpResponseForbidden("You do not have permission to view this page.")

    context = {
        'installations': installations_queryset, # This will be the 'installations' variable in your template
        'page_title': page_title,
    }
    return render(request, 'accounts/installer/installer_dashboard.html', context)


# --- Re-integrated create_installation_view with assignment and notification logic ---
@role_required('1')  # Apply the custom role_required decorator for role_id '1'
def create_installation_view(request):
    """
    Handles the creation of a new Installation and its associated Customer.
    If an installer is assigned in the form, the status is set to PENDING_ACCEPTANCE
    and an in-app notification is sent.
    """
    if request.method == 'POST':
        form = InstallationForm(request.POST)
        if form.is_valid():
            print("[DEBUG] Form is valid")
            try:
                # Save the form instance without committing to the database yet
                installation = form.save(commit=False)

                # Get assigned installer details from the form
                assigned_user = form.cleaned_data.get('assigned_installer')
                installer_profile = form.cleaned_data.get('installer')

                # Logic to handle status transition and assignment
                if assigned_user or installer_profile:
                    # If an installer is selected, set status to PENDING_ACCEPTANCE
                    installation.status = 'PENDING_ACCEPTANCE'
                    # Set assignment expiration (e.g., 24 hours from now)
                    installation.assignment_expires_at = timezone.now() + datetime.timedelta(hours=24)

                    # Ensure assigned_installer matches installer_profile's user if both are provided
                    if assigned_user and installer_profile and installer_profile.user != assigned_user:
                        form.add_error('installer', "Selected installer company profile must match the assigned user.")
                        print("[ERROR] Installer profile user mismatch during form processing.")
                        return render(request, 'accounts/admin/admin_installation_page.html', context={'form': form})
                    
                    # If only installer_profile is provided, use its linked user as assigned_installer
                    if installer_profile and not assigned_user:
                        installation.assigned_installer = installer_profile.user
                    elif assigned_user: # If assigned_user is explicitly provided (and maybe installer_profile too)
                        installation.assigned_installer = assigned_user
                    
                    # Ensure installer_profile is set on the installation if it was selected
                    installation.installer = installer_profile
                else:
                    # If no installer is assigned, status remains SUBMITTED (default from model)
                    installation.status = 'SUBMITTED'
                    installation.assignment_expires_at = None # Ensure it's null if not pending

                installation.save() # Now save the installation object with updated fields

                # Create in-app notification if an installer was assigned and status is PENDING_ACCEPTANCE
                if installation.status == 'PENDING_ACCEPTANCE' and installation.assigned_installer:
                    Notification.objects.create(
                        user=installation.assigned_installer, # Notify the CustomUser
                        message=f"You have been assigned a new installation job: {installation.installation_id} for {installation.customer.name} at {installation.address}. Please respond within 24 hours.",
                        related_installation=installation
                    )
                    print(f"[DEBUG] Notification sent to {installation.assigned_installer.username}.")

                print("[DEBUG] Installation created/assigned successfully. Redirecting to detail page.")
                # Redirect to the detail page of the newly created/assigned installation
                return redirect('installation_detail', installation_id=installation.installation_id)
            except Exception as e:
                form.add_error(None, f"An error occurred during saving: {e}")
                print(f"[ERROR] Saving error: {e}")
        else:
            print(f"[ERROR] Form errors: {form.errors.as_json()}") # More detailed error logging
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

# --- Updated installation_detail with comprehensive permission checks ---
@login_required # Assuming role_required does not cover login_required
# @role_required('2') # This decorator might be too restrictive if admins should also see it
def installation_detail(request, installation_id):
    """
    Displays the detailed information for a single installation job.
    Includes comprehensive permission checks.
    """
    installation = get_object_or_404(Installation, installation_id=installation_id)

    # Permission Checks:
    # 1. Allow if the user is an Admin
    if request.user.role == '1': # Assuming '1' is the role code for Admin
        pass # Admin can view anything
    # 2. Allow if the user is an Installer AND is assigned to this job
    elif request.user.role == '2': # Assuming '2' is the role code for Installer
        is_assigned_directly = (installation.assigned_installer == request.user)
        is_assigned_via_profile = False
        if installation.installer: # Check if installer profile exists on the installation
            is_assigned_via_profile = (installation.installer.user == request.user) # Check if that profile's user matches current user

        if not (is_assigned_directly or is_assigned_via_profile):
            # If the installer is not directly assigned AND not assigned via their profile, deny access
            return HttpResponseForbidden("You do not have permission to view this installation.")
    # 3. Deny access if user is neither Admin nor an assigned Installer
    else:
        return HttpResponseForbidden("You do not have permission to view this installation.")

    context = {
        'installation': installation
    }
    # It seems your template for installation_detail is installer_dashboard_layout.html
    # so keeping consistency here.
    return render(request, 'accounts/installer/installer_installation_detail.html', context)


# --- View to handle acceptance/rejection (you'll need to create URLs for these) ---
@login_required
@role_required('2')
def handle_installation_response(request, installation_id, action):
    """
    Handles an installer's acceptance or rejection of an installation job.
    """
    installation = get_object_or_404(Installation, installation_id=installation_id)

    # --- Security checks ---
    is_assigned_to_user = (installation.assigned_installer == request.user)
    is_assigned_to_profile_user = False
    if installation.installer:
        is_assigned_to_profile_user = (installation.installer.user == request.user)

    if not (is_assigned_to_user or is_assigned_to_profile_user) or \
       installation.status != 'PENDING_ACCEPTANCE':
        messages.error(request, "You are not authorized to perform this action or the job status is not pending.")
        return redirect(request.META.get('HTTP_REFERER', 'installation_list'))

    if request.method == 'POST':
        if action == 'accept':
            installation.status = 'ACCEPTED'
            installation.save()
            messages.success(request, "Job accepted successfully!")
            
        elif action == 'reject':
            installation.status = 'REJECTED'
            installation.save()
            messages.success(request, "Job rejected successfully!")

        return redirect(request.META.get('HTTP_REFERER', 'installation_list'))

    messages.error(request, "Invalid request method or action.")
    return redirect(request.META.get('HTTP_REFERER', 'installation_list'))


