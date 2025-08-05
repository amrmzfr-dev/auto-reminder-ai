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
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import ContractorRegisterForm
from .models import InstallerProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy
from .forms import InstallerProfileForm 
from django.utils.decorators import method_decorator
from .forms import AdminRegistrationForm

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
def admin_register_view(request):
    """
    Admin-only registration view. Handles account creation with role 'Admin'.
    """
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('admin_dashboard')
    else:
        form = AdminRegistrationForm()

    return render(request, 'accounts/admin_register.html', {'form': form})


def installer_register(request):
    if request.method == 'POST':
        form = ContractorRegisterForm(request.POST)
        if form.is_valid():
            # Create user account
            user = form.save(commit=False)
            user.role = '2'  # Installer
            user.is_active = True  # Optional: mark inactive for approval flow
            user.save()

            # Create minimal installer profile
            InstallerProfile.objects.create(
                user=user,
                company_name=form.cleaned_data['company_name'],
                pic_name=form.cleaned_data['pic_name'],
                pic_contact_number=form.cleaned_data['pic_contact_number'],
                pic_email=form.cleaned_data['pic_email'],
                registration_status='incomplete'  # Add this field if not already in your model
            )

            # Optionally auto-login the user
            # login(request, user)

            return redirect('login')  # Or use 'complete_profile' for onboarding continuation
    else:
        form = ContractorRegisterForm()

    left_fields = ['username','company_name','password1', 'password2']
    right_fields = [ 'pic_name', 'pic_email', 'pic_contact_number', 'agree_terms']

    return render(
        request,
        'accounts/installer/installer_register.html',
        {
            'form': form,
            'left_fields': left_fields,
            'right_fields': right_fields,
        }
    )

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

    try:
        profile = InstallerProfile.objects.get(user=request.user)
        if profile.registration_status == 'incomplete':
            messages.warning(
                request,
                "⚠️ Your registration is incomplete. Please complete your company profile to proceed."
            )
    except InstallerProfile.DoesNotExist:
        messages.error(request, "Installer profile not found. Please contact support.")
        return redirect('logout')  # Or another fallback action

    return render(request, 'accounts/installer/installer_dashboard.html')

@method_decorator([login_required, role_required('2')], name='dispatch')
class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = InstallerProfile
    template_name = 'accounts/installer/profile_detail.html'

    def get_object(self):
        return self.request.user.installerprofile


@method_decorator([login_required, role_required('2')], name='dispatch')
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = InstallerProfile
    form_class = InstallerProfileForm
    template_name = 'accounts/installer/profile_edit.html'
    success_url = reverse_lazy('company_profile')

    def get_object(self):
        return self.request.user.installerprofile
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
    installers = User.objects.filter(role='2').select_related('installerprofile')  # Correct related_name
    return render(request, 'accounts/admin/admin_installer_list.html', {'installers': installers})
