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
from ..models import Customer, ChargerModel, InstallerProfile, State
from ..models import Installation # Your Installation model
from django.db import models # Needed for Q objects in installation_list
from django.db.models import Count, Q

# Import your InstallationForm
from ..forms import InstallationForm # Adjust this import path if your form is elsewhere
# Import your role_required decorator
from ..decorators import role_required
from ..services import InstallationService

import random

# User = get_user_model() # Typically not needed if CustomUser is directly imported
# --- END IMPORTANT IMPORTS ---


@login_required
def installation_list_view(request):
    """
    Displays a list of installation jobs and status statistics based on the logged-in user's role.
    """
    # Use service layer to get installations and determine template
    installations_queryset = InstallationService.get_installations_for_user(request.user)
    
    if request.user.role == '1':  # Admin
        page_title = "Admin Dashboard - All Installations"
        template_name = 'accounts/admin/admin_installation_list.html'
    elif request.user.role == '2':  # Installer
        try:
            installer_profile = InstallerProfile.objects.get(user=request.user)
            page_title = f"Installer Dashboard - {installer_profile.company_name} Installations"
        except InstallerProfile.DoesNotExist:
            page_title = "Installer Dashboard - Your Installations (Profile Missing)"
        template_name = 'accounts/installer/installer_installation_list.html'
    else:
        # Deny access for any other role
        return HttpResponseForbidden("You do not have permission to view this page.")

    # Get status counts and total installations
    status_counts = InstallationService.get_status_counts()
    total_installations = installations_queryset.count()

    # Prepare the context
    context = {
        'installations': installations_queryset,
        'page_title': page_title,
        'total_installations': total_installations,
        'status_counts': status_counts,
        'STATUS_CHOICES': Installation.STATUS_CHOICES,
    }

    # Render the appropriate template based on user role
    return render(request, template_name, context)

def get_customer_state_obj(customer_state_str):
    """
    Convert a Customer.state string to the corresponding State instance
    based on your State table.
    """
    state_mapping = {
        'Selangor': 'Central 2',
        'Kuala Lumpur': 'Central 1',
        'Putrajaya': 'Central 1',
        'Perak': 'Northern',
        'Kedah': 'Northern',
        'Perlis': 'Northern',
        'Penang': 'Northern',
        'Negeri Sembilan': 'Southern',
        'Melaka': 'Southern',
        'Johor': 'Southern',
        'Pahang': 'East Coast',
        'Terengganu': 'East Coast',
        'Kelantan': 'East Coast',
        'Sabah': "East M'sia",
        'Sarawak': "East M'sia",
    }
    state_code = state_mapping.get(customer_state_str)
    if not state_code:
        return None
    try:
        return State.objects.get(code=state_code)
    except State.DoesNotExist:
        return None


# --- Helper function for automatic installer assignment ---
def auto_assign_installer(installation):
    """
    Automatically assign an installer based on:
    1. Same state priority (operational_states of installer)
    2. Fewer past jobs
    3. Round-robin fairness among equal candidates
    """
    # Step 0: Get the installation's customer state object
    state_obj = get_customer_state_obj(installation.customer.state)
    customer_state = installation.customer.state
    # Step 1: Filter installers who operate in this state
    if state_obj:
        state_installers = CustomUser.objects.filter(
            role='2',  # '2' = Installer
            installerprofile__operational_states=state_obj
        ).distinct()
    else:
        # Fallback: pick any installer
        state_installers = CustomUser.objects.filter(role='2').distinct()

    if not state_installers.exists():
        # Safety fallback
        state_installers = CustomUser.objects.filter(role='2').distinct()

    # Step 2: Count past jobs per installer
    installers_with_jobs = []
    for installer in state_installers:
        job_count = Installation.objects.filter(assigned_installer=installer).count()
        installers_with_jobs.append((installer, job_count))

    # Step 3: Sort ascending by number of jobs
    installers_with_jobs.sort(key=lambda x: x[1])

    # Step 4: Candidates with the least jobs
    min_jobs = installers_with_jobs[0][1]
    candidates = [inst for inst, jobs in installers_with_jobs if jobs == min_jobs]

    # Step 5: Random choice among candidates (fairness / round-robin)
    selected_installer = random.choice(candidates)

    print(f"[DEBUG] Auto-assign installer for Installation {installation.installation_id}")
    print(f"        Customer state: {customer_state}")
    print(f"        Candidate installers & past jobs: {[ (i.username,j) for i,j in installers_with_jobs ]}")
    print(f"        Chosen installer: {selected_installer.username}")

    return selected_installer


# --- Main view ---
@role_required('1')  # Admin only
def create_installation_view(request):
    """
    Handles the creation of a new Installation.
    Automatically assigns an installer if none is manually selected,
    based on customer state, past jobs, and fairness.
    """
    if request.method == 'POST':
        form = InstallationForm(request.POST)
        if form.is_valid():
            try:
                # Save form without committing yet
                installation = form.save(commit=False)

                # Get manual assignment from form
                assigned_user = form.cleaned_data.get('assigned_installer')
                installer_profile = form.cleaned_data.get('installer')

                if assigned_user or installer_profile:
                    # Manual assignment
                    if assigned_user and installer_profile and installer_profile.user != assigned_user:
                        form.add_error(
                            'installer',
                            "Selected installer company profile must match the assigned user."
                        )
                        return render(
                            request,
                            'accounts/admin/admin_installation_page.html',
                            {'form': form}
                        )

                    installation.status = 'PENDING_ACCEPTANCE'
                    installation.assignment_expires_at = timezone.now() + timezone.timedelta(hours=24)

                    if installer_profile and not assigned_user:
                        installation.assigned_installer = installer_profile.user
                    elif assigned_user:
                        installation.assigned_installer = assigned_user

                    installation.installer = installer_profile

                else:
                    # AUTO ASSIGN installer
                    selected_installer = auto_assign_installer(installation)
                    installation.assigned_installer = selected_installer
                    installation.status = 'PENDING_ACCEPTANCE'
                    installation.assignment_expires_at = timezone.now() + timezone.timedelta(hours=24)

                    # Attach installer_profile if exists
                    try:
                        installation.installer = selected_installer.installerprofile
                    except InstallerProfile.DoesNotExist:
                        installation.installer = None

                # Save installation
                installation.save()

                # Redirect to detail page
                return redirect('installation_detail', installation_id=installation.installation_id)

            except Exception as e:
                form.add_error(None, f"An error occurred during saving: {e}")

        else:
            print(f"[ERROR] Form errors: {form.errors.as_json()}")

    else:
        form = InstallationForm()

    return render(request, 'accounts/admin/admin_installation_page.html', {'form': form})


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
