# views/auth_views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from ..forms import ContractorRegisterForm, AdminRegistrationForm
from ..models import InstallerProfile

# Get the custom user model, which is likely where the 'role' field is defined.
# This ensures compatibility if a custom user model is used instead of Django's default.
User = get_user_model()

# -----------------------------------------------
# 🔐 Login View with Role-Based Redirection
# -----------------------------------------------
def login_view(request):
    """
    Handles user login, authenticates credentials, and redirects
    to a role-specific dashboard upon successful login.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the login page or redirects to a dashboard.
    """
    if request.method == 'POST':
        # Retrieve username and password from the POST request
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user with the provided credentials
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # If authentication is successful, log the user in
            login(request, user)

            # Redirect the user to the appropriate dashboard based on their role
            if hasattr(user, 'role') and user.role == '1':  # Admin role
                return redirect('admin_dashboard')
            elif hasattr(user, 'role') and user.role == '2':  # Installer role
                return redirect('installer_dashboard')
            else:
                # Fallback redirect for any other roles or default users
                return redirect('admin_dashboard')

        else:
            # If authentication fails, render the login page with an error message
            return render(request, 'accounts/login.html', {
                'error': 'Invalid username or password.'
            })

    # Render the login page for GET requests
    return render(request, 'accounts/login.html')

# -----------------------------------------------
# 👤 Register View for Admins
# -----------------------------------------------
def admin_register_view(request):
    """
    Admin-only registration view. Handles account creation with role 'Admin'.
    This view uses a dedicated AdminRegistrationForm.
    """
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            # Save the new user and assign the default admin role from the form's logic.
            user = form.save()
            # Log the new admin user in automatically after registration.
            login(request, user)
            return redirect('admin_dashboard')
    else:
        form = AdminRegistrationForm()

    return render(request, 'accounts/admin_register.html', {'form': form})

# -----------------------------------------------
# 👷 Register View for Installers
# -----------------------------------------------
def installer_register(request):
    """
    Installer registration view. Creates a new user with role '2' (Installer)
    and an associated InstallerProfile.
    """
    if request.method == 'POST':
        form = ContractorRegisterForm(request.POST)
        if form.is_valid():
            # Create user account but don't save to the database yet.
            user = form.save(commit=False)
            # Assign the 'Installer' role.
            user.role = '2'
            # Set the user as active. This can be changed for an approval workflow.
            user.is_active = True
            user.save()

            # Create a minimal installer profile using data from the registration form.
            InstallerProfile.objects.create(
                user=user,
                company_name=form.cleaned_data['company_name'],
                pic_name=form.cleaned_data['pic_name'],
                pic_contact_number=form.cleaned_data['pic_contact_number'],
                pic_email=form.cleaned_data['pic_email'],
                # Set a status to indicate the profile is not yet complete.
                registration_status='incomplete'
            )

            # Redirect to the login page for the new user to sign in.
            return redirect('login')
    else:
        form = ContractorRegisterForm()

    # Define fields for a two-column layout in the template.
    left_fields = ['username', 'company_name', 'password1', 'password2']
    right_fields = ['pic_name', 'pic_email', 'pic_contact_number', 'agree_terms']

    return render(
        request,
        'accounts/installer/installer_register.html',
        {
            'form': form,
            'left_fields': left_fields,
            'right_fields': right_fields,
        }
    )

# -----------------------------------------------
# 🚪 Logout View
# -----------------------------------------------
def logout_view(request):
    """
    Logs the current user out and redirects them to the login page.
    """
    logout(request)
    return redirect('login')