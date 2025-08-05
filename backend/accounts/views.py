# Import necessary modules from Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from functools import wraps # Used for preserving metadata of decorated functions
from .models import CustomUser
from .models import Task
from .forms import TaskForm
from .forms import InstallerRegistrationForm
from .models import InstallerProfile

# Get the custom user model, which is likely where the 'role' field is defined.
# This ensures compatibility if a custom user model is used instead of Django's default.
User = get_user_model()

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
        @wraps(view_func) # Preserves the original function's metadata (e.g., name, docstring)
        @login_required # Ensures the user is logged in before checking their role
        def _wrapped_view(request, *args, **kwargs):
            # Check if the logged-in user's role matches the required role
            if hasattr(request.user, 'role') and request.user.role == required_role:
                return view_func(request, *args, **kwargs) # If roles match, execute the view
            # If roles do not match, return an HTTP 403 Forbidden response
            return HttpResponseForbidden("❌ Access Denied")
        return _wrapped_view
    return decorator

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
# 👤 Register View with Role Assignment
# -----------------------------------------------
def register_view(request):
    """
    Handles user registration, validates the data, creates a new user with a specified role,
    and logs them in before redirecting to their role-specific dashboard.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the registration page or redirects to a dashboard.
    """
    if request.method == 'POST':
        # Get registration data from the POST request
        username = request.POST['username']
        password1 = request.POST['password']
        password2 = request.POST['password2']
        role = request.POST.get('role')  # Expects 'role' to be in the form data

        # Validate the passwords and username
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        elif role not in ['1', '2']: # Ensure the selected role is valid
            messages.error(request, 'Invalid role selected')
        else:
            # Create a new user with the provided details and role
            user = User.objects.create_user(username=username, password=password1, role=role)
            # Log the new user in immediately
            login(request, user)

            # Redirect post-registration based on the assigned role
            if user.role == '1':
                return redirect('admin_dashboard')
            elif user.role == '2':
                return redirect('installer_dashboard')
            else:
                return redirect('admin_dashboard')

    # Render the registration page for GET requests or if validation fails
    return render(request, 'accounts/register.html')


def installer_register(request):
    if request.method == 'POST':
        form = InstallerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = '2'  # Installer
            user.save()

            InstallerProfile.objects.create(
                user=user,
                company_name=form.cleaned_data['company_name'],
                company_ssm_number=form.cleaned_data['company_ssm_number'],
                operational_state=form.cleaned_data['operational_state'],
                pic_name=form.cleaned_data['pic_name'],
                pic_designation=form.cleaned_data['pic_designation'],
                pic_contact_number=form.cleaned_data['pic_contact_number'],
                company_address=form.cleaned_data.get('company_address', ''),
                year_established=form.cleaned_data.get('year_established'),
                epf_contributors=form.cleaned_data.get('epf_contributors'),
                is_st_registered=form.cleaned_data.get('is_st_registered', False),
                contractor_license_class=form.cleaned_data.get('contractor_license_class'),
                is_cidb_registered=form.cleaned_data.get('is_cidb_registered', False),
                cidb_category=form.cleaned_data.get('cidb_category', ''),
                cidb_grade=form.cleaned_data.get('cidb_grade', ''),
                is_sst_registered=form.cleaned_data.get('is_sst_registered', False),
                sst_number=form.cleaned_data.get('sst_number', ''),
                has_insurance=form.cleaned_data.get('has_insurance', False),
                has_coi_history=form.cleaned_data.get('has_coi_history', False),
            )

            return redirect('login')
    else:
        form = InstallerRegistrationForm()
    return render(request, 'accounts/installer/installer_register.html', {'form': form})

# 🚪 Logout View
def logout_view(request):
    """
    Logs the current user out and redirects them to the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to the login page.
    """
    logout(request)
    return redirect('login')


# -----------------------------------------------
# 📊 Admin Dashboard View
# -----------------------------------------------
@role_required('1')  # Only users with role '1' (Admin) can access this view
def dashboard_view(request):
    """
    Displays the admin dashboard with task statistics.
    Requires the user to be logged in and have an 'Admin' role.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the admin dashboard template with task data.
    """
    # Retrieve all tasks from the database, ordered by creation date
    tasks = Task.objects.all().order_by('created_at')

    # Calculate various task statistics
    total_tasks = tasks.count()
    in_progress = tasks.filter(status="In Progress").count()
    pending = tasks.filter(status="Pending").count()
    completed = tasks.filter(status="Completed").count()

    # Calculate the completion rate, avoiding division by zero
    completion_rate = int((completed / total_tasks) * 100) if total_tasks > 0 else 0

    # Prepare the context dictionary for the template
    context = {
        'tasks': tasks,
        'total_tasks': total_tasks,
        'in_progress': in_progress,
        'pending': pending,
        'completion_rate': completion_rate,
    }

    # Render the admin dashboard template with the calculated context
    return render(request, 'accounts/admin/admin_dashboard.html', context)

# ------------------------------
# 👷 Installer Dashboard View
# ------------------------------
@role_required('2')  # Only users with role '2' (Installer) can access this view
def installer_dashboard_view(request):
    """
    Displays a simple dashboard for installer users.
    Requires the user to be logged in and have an 'Installer' role.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the installer dashboard template.
    """
    # Renders the installer dashboard template.
    # This view currently does not pass any specific context data,
    # but could be extended to show installer-specific tasks.
    return render(request, 'accounts/installer/installer_dashboard.html')


# -----------------------------------------------
# ➕ Add Task View (Admin Only)
# -----------------------------------------------
@login_required # Ensures the user is logged in
@role_required('1') # Consider adding this if only admins should add tasks
def add_task(request):
    """
    Handles the creation of a new task.
    Requires the user to be logged in. Access control for role can be added
    via the @role_required decorator if needed.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the task form or redirects to the admin dashboard.
    """
    if request.method == 'POST':
        # Create a TaskForm instance with the POST data and any uploaded files
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            # If the form is valid, save the new task to the database
            form.save()
            # Redirect to the admin dashboard after saving
            return redirect('admin_dashboard')
    else:
        # For GET requests, create an empty form
        form = TaskForm()
        
    # Render the task form template
    return render(request, 'accounts/admin/task_form.html', {
        'form': form,
        'form_title': 'Add Task',
        'submit_label': 'Create Task',
    })


# -----------------------------------------------
# ✏️ Edit Task View (Admin Only)
# -----------------------------------------------
@login_required # Ensures the user is logged in
@role_required('1') # Consider adding this if only admins should edit tasks
def edit_task(request, pk):
    """
    Handles the editing of an existing task.
    Requires the user to be logged in. Access control for role can be added
    via the @role_required decorator if needed.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the task to be edited.

    Returns:
        HttpResponse: Renders the task form or redirects to the admin dashboard.
    """
    # Get the task object to be edited, or return a 404 error if it doesn't exist
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        # Create a TaskForm instance with POST data and the existing task instance
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            # If the form is valid, save the updated task
            form.save()
            # Redirect to the admin dashboard after updating
            return redirect('admin_dashboard')
    else:
        # For GET requests, create a form pre-populated with the task's data
        form = TaskForm(instance=task)
        
    # Render the task form template for editing
    return render(request, 'accounts/admin/task_form.html', {
        'form': form,
        'form_title': 'Edit Task',
        'submit_label': 'Update Task',
    })


# -----------------------------------------------
# 🗑️ Delete Task View (Admin Only)
# -----------------------------------------------
@login_required # Ensures the user is logged in
@role_required('1') # Consider adding this if only admins should delete tasks
def delete_task(request, pk):
    """
    Handles the deletion of a task.
    Requires the user to be logged in. Access control for role can be added
    via the @role_required decorator if needed.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the task to be deleted.

    Returns:
        HttpResponse: Redirects to the admin dashboard.
    """
    # Get the task object to be deleted, or return a 404 error if it doesn't exist
    task = get_object_or_404(Task, pk=pk)
    # Delete the task from the database
    task.delete()
    # Redirect to the admin dashboard after deletion
    return redirect('admin_dashboard')

@role_required('1')  # Only Admins can access this
def installer_list_view(request):
    installers = CustomUser.objects.filter(role='2')
    context = {
        'installers': installers,
    }
    return render(request, 'accounts/admin/admin_installer_list.html', context)