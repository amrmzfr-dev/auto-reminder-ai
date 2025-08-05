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

    # Task CRUD
    path('task/add/', views.add_task, name='add_task'),
    path('task/edit/<int:pk>/', views.edit_task, name='edit_task'),
    path('task/delete/<int:pk>/', views.delete_task, name='delete_task'),
]
