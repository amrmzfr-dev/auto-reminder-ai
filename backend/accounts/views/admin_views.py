# views/admin_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from functools import wraps
from ..models import Task, Installation, Notification
from ..forms import TaskForm


# 🌱 NEW imports for Channels
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import datetime
from django.contrib import messages

# Get the custom user model.
User = get_user_model()

# -----------------------------------------------
# 🛡️ Role-Based Access Control Decorator
# -----------------------------------------------
def role_required(required_role):
    """
    Restrict access to views based on user's role.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'role') and request.user.role == required_role:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("❌ Access Denied")
        return _wrapped_view
    return decorator


# -----------------------------------------------
# 📊 Admin Dashboard View
# -----------------------------------------------
@role_required('1')
def dashboard_view(request):
    tasks = Task.objects.all().order_by('created_at')

    total_tasks = tasks.count()
    in_progress = tasks.filter(status="In Progress").count()
    pending = tasks.filter(status="Pending").count()
    completed = tasks.filter(status="Completed").count()

    completion_rate = int((completed / total_tasks) * 100) if total_tasks > 0 else 0
    
    # 🔔 Get notification count for the current user
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    
    # 🔔 Create a test notification if none exist (for testing purposes)
    if unread_notifications == 0:
        # Check if user has any notifications at all
        total_notifications = Notification.objects.filter(user=request.user).count()
        if total_notifications == 0:
            # Create a test notification
            Notification.objects.create(
                user=request.user,
                message="🔔 Welcome! This is your first notification. The system is working!",
                related_installation=None
            )
            unread_notifications = 1

    context = {
        'tasks': tasks,
        'total_tasks': total_tasks,
        'in_progress': in_progress,
        'pending': pending,
        'completion_rate': completion_rate,
        'unread_notifications': unread_notifications,  # 🔔 Add notification count
    }
    return render(request, 'accounts/admin/admin_dashboard.html', context)


# -----------------------------------------------
# ➕ Add Task View (Admin Only)
# -----------------------------------------------
@role_required('1')
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save()

            # 🌱 Flash message for yourself
            messages.success(request, f"✅ Task '{task.title}' added successfully!")

            # 🌱 Create notifications for all admin users
            admin_users = User.objects.filter(role='1')
            print(f"🔔 Found {admin_users.count()} admin users")
            
            for admin_user in admin_users:
                print(f"🔔 Creating notification for admin: {admin_user.username}")
                Notification.objects.create(
                    user=admin_user,
                    message=f"✅ New Task Added: {task.title} by {request.user.username}",
                    priority=task.priority,
                    related_installation=None,
                    related_task=task
                )
                print(f"🔔 Notification created for {admin_user.username}")

            # 🌱 Send real-time notification to all admins
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "admins",  # group name
                {
                    "type": "send_notification",
                    "message": f"✅ New Task Added: {task.title} by {request.user.username}",
                    "timestamp": datetime.datetime.now().strftime("%d %b %Y %H:%M"),
                },
            )
            return redirect('admin_dashboard')
    else:
        form = TaskForm()

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
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            old_title = task.title
            form.save()
            
            # 🌱 Create notifications for all admin users
            admin_users = User.objects.filter(role='1')
            for admin_user in admin_users:
                if admin_user != request.user:  # Don't notify yourself
                    Notification.objects.create(
                        user=admin_user,
                        message=f"✏️ Task Updated: '{old_title}' by {request.user.username}",
                        priority=task.priority,
                        related_installation=None,
                        related_task=task
                    )
            
            # 🌱 Send real-time notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "admins",
                {
                    "type": "send_notification",
                    "message": f"✏️ Task Updated: '{old_title}' by {request.user.username}",
                    "timestamp": datetime.datetime.now().strftime("%d %b %Y %H:%M"),
                },
            )
            
            return redirect('admin_dashboard')
    else:
        form = TaskForm(instance=task)

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
    task = get_object_or_404(Task, pk=pk)
    task_title = task.title
    task.delete()

# -----------------------------------------------
# 👁️ Task Detail View (Admin Only)
# -----------------------------------------------
@role_required('1')
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'accounts/admin/task_detail.html', {
        'task': task
    })
    
    # 🌱 Create notifications for all admin users
    admin_users = User.objects.filter(role='1')
    for admin_user in admin_users:
        if admin_user != request.user:  # Don't notify yourself
            Notification.objects.create(
                user=admin_user,
                message=f"🗑️ Task Deleted: '{task_title}' by {request.user.username}",
                priority=task.priority,
                related_installation=None
            )
    
    # 🌱 Send real-time notification
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "admins",
        {
            "type": "send_notification",
            "message": f"🗑️ Task Deleted: '{task_title}' by {request.user.username}",
            "timestamp": datetime.datetime.now().strftime("%d %b %Y %H:%M"),
        },
    )
    
    return redirect('admin_dashboard')


# -----------------------------------------------
# 📝 Installer List View (Admin Only)
# -----------------------------------------------
@role_required('1')
def installer_list_view(request):
    installers = User.objects.filter(role='2').select_related('installerprofile')
    return render(request, 'accounts/admin/admin_installer_list.html', {'installers': installers})


@role_required('1')
def installation_list_view(request):
    installations = Installation.objects.select_related('customer', 'charger_model').order_by('-created_at')
    return render(request, 'accounts/admin/admin_installation_list.html', {
        'installations': installations
    })


# -----------------------------------------------
# 📄 Notifications Page (lists user's notifications)
# -----------------------------------------------
@login_required
def notifications_page_view(request):
    unread = Notification.objects.filter(user=request.user, is_read=False).count()
    return render(request, 'accounts/notifications.html', {
        'unread_notifications': unread,
    })


# -----------------------------------------------
#  Notification Views
# -----------------------------------------------
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def notification_list_view(request):
    """Get all notifications for the current user (temporarily no auth to diagnose 403)."""
    user = request.user if request.user.is_authenticated else None
    print(f"🔔 Notification request from user: {user.username if user else 'ANON'}")
    
    if user is None:
        return JsonResponse({'notifications': [], 'unread_count': 0})
    
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    print(f"🔔 Found {notifications.count()} notifications for user")
    
    notification_data = []
    for notification in notifications:
        notification_data.append({
            'id': notification.id,
            'message': notification.message,
            'is_read': notification.is_read,
            'priority': notification.priority,
            'created_at': notification.created_at.strftime('%d %b %Y %H:%M'),
            'related_installation': notification.related_installation.installation_id if notification.related_installation else None,
            'related_task': notification.related_task.id if notification.related_task else None
        })
        print(f"🔔 Notification: {notification.message}")
    
    unread_count = notifications.filter(is_read=False).count()
    print(f"🔔 Unread count: {unread_count}")
    
    return JsonResponse({
        'notifications': notification_data,
        'unread_count': unread_count
    })

@csrf_exempt
@login_required
def mark_notification_read_view(request, notification_id):
    """Mark a specific notification as read"""
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.mark_as_read()
            return JsonResponse({'status': 'success'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
@login_required
def mark_all_notifications_read_view(request):
    """Mark all notifications as read for the current user"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
@login_required
def delete_notification_view(request, notification_id):
    """Delete a specific notification belonging to the current user"""
    if request.method in ['POST', 'DELETE']:
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.delete()
            return JsonResponse({'status': 'success'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
@login_required
def clear_notifications_view(request):
    """Delete all notifications for the current user"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
