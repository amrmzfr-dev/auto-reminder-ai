from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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

@login_required(login_url='login')  # 🔐 force login if not authenticated
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html', {
        'user': request.user  # send user data to the template
    })