# views/admin_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from functools import wraps
from ..models import Task
from ..forms import TaskForm

# Get the custom user model.
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


# -----------------------------------------------
# 📊 Admin Dashboard View
# -----------------------------------------------
@role_required('1')  # Only users with role '1' (Admin) can access this view
def dashboard_view(request):
    """
    Displays the admin dashboard with task statistics.
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

# -----------------------------------------------
# ➕ Add Task View (Admin Only)
# -----------------------------------------------
@role_required('1')
def add_task(request):
    """
    Handles the creation of a new task.
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
@role_required('1')
def edit_task(request, pk):
    """
    Handles the editing of an existing task.
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
@role_required('1')
def delete_task(request, pk):
    """
    Handles the deletion of a task.
    """
    # Get the task object to be deleted, or return a 404 error if it doesn't exist
    task = get_object_or_404(Task, pk=pk)
    # Delete the task from the database
    task.delete()
    # Redirect to the admin dashboard after deletion
    return redirect('admin_dashboard')

# -----------------------------------------------
# 📝 Installer List View (Admin Only)
# -----------------------------------------------
@role_required('1')  # Only Admins can access this
def installer_list_view(request):
    """
    Displays a list of all registered installers for the admin.
    """
    # Retrieve all users with role '2' (Installers) and pre-fetch their profiles for efficiency.
    installers = User.objects.filter(role='2').select_related('installerprofile')
    return render(request, 'accounts/admin/admin_installer_list.html', {'installers': installers})