from django.urls import path
from . import views
from .views import ProfileDetailView, ProfileUpdateView

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/admin/', views.admin_register_view, name='admin_register'),
    path('register_installer/', views.installer_register, name='installer_register'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('admin_dashboard/', views.dashboard_view, name='admin_dashboard'),
    path('installer_dashboard/', views.installer_dashboard_view, name='installer_dashboard'),
    path('company-profile/', ProfileDetailView.as_view(), name='company_profile'),
    path('company-profile/edit/', ProfileUpdateView.as_view(), name='edit_company_profile'),

    # Installer List (Admin only)
    path('admin/installers/', views.installer_list_view, name='installer_list'),
    path('installations/', views.installation_page_view, name='installation_page_view'),
    path('installations/create/', views.create_installation_view, name='create_installation'),
    path('admin/installations/', views.installation_list_view, name='installation_list'),
    # Task CRUD
    path('task/add/', views.add_task, name='add_task'),
    path('task/<int:pk>/', views.task_detail, name='task_detail'),
    path('task/edit/<int:pk>/', views.edit_task, name='edit_task'),
    path('task/delete/<int:pk>/', views.delete_task, name='delete_task'),
    path('task/<int:task_id>/update-status/', views.update_task_status_view, name='update_task_status'),

    # TEST
    path('upload/', views.upload_file, name='upload_file'),
    
    # 🔔 Notification URLs (Admin only)
    path('notifications/', views.notification_list_view, name='admin_notifications'),
    path('notifications/page/', views.notifications_page_view, name='notifications_page'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read_view, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read_view, name='mark_all_notifications_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification_view, name='delete_notification'),
    path('notifications/clear/', views.clear_notifications_view, name='clear_notifications'),

    # Catch-all installation detail routes MUST be last
    path('<str:installation_id>/', views.installation_detail, name='installation_detail'),
    path('<str:installation_id>/<str:action>/', views.handle_installation_response, name='handle_installation_response'),
]
