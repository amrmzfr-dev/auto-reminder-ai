from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm

# 🔐 Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  # change if you want a different landing page
        else:
            # Invalid credentials: send error message to template
            return render(request, 'accounts/login.html', {
                'error': 'Invalid username or password.'
            })

    # GET method: just show login page
    return render(request, 'accounts/login.html')


# 👤 Register View
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, 'Passwords do not match')
        else:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            else:
                # Create user and log them in immediately
                user = User.objects.create_user(username=username, password=password1)
                login(request, user)
                return redirect('/')
    return render(request, 'accounts/register.html')


# 🚪 Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    tasks = Task.objects.all().order_by('due_date')
    return render(request, 'accounts/dashboard.html', {'tasks': tasks})


def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)
    return render(request, 'accounts/task_form.html', {'form': form, 'action': 'Edit'})

@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TaskForm()
    return render(request, 'accounts/task_form.html', {'form': form, 'action': 'Add'})

@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect('dashboard')