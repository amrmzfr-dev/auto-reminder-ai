# accounts/services/installation_service.py
from django.db.models import Count, Q
from ..models import Installation, InstallerProfile


class InstallationService:
    """
    Service class to centralize installation-related business logic
    and eliminate duplicate code across views.
    """
    
    @staticmethod
    def get_installations_for_user(user):
        """
        Get installations based on user role and permissions.
        
        Args:
            user: The authenticated user
            
        Returns:
            QuerySet: Filtered installations for the user
        """
        if user.role == '1':  # Admin
            return Installation.objects.all().order_by('-created_at')
        elif user.role == '2':  # Installer
            try:
                installer_profile = InstallerProfile.objects.get(user=user)
                return Installation.objects.filter(
                    Q(assigned_installer=user) | Q(installer=installer_profile)
                ).order_by('-created_at')
            except InstallerProfile.DoesNotExist:
                return Installation.objects.filter(assigned_installer=user).order_by('-created_at')
        else:
            return Installation.objects.none()
    
    @staticmethod
    def get_status_counts():
        """
        Get status counts for all installations.
        
        Returns:
            dict: Status counts
        """
        status_counts_queryset = Installation.objects.values('status').annotate(count=Count('status'))
        return {item['status']: item['count'] for item in status_counts_queryset}
    
    @staticmethod
    def get_installer_installations(installer_profile):
        """
        Get installations for a specific installer.
        
        Args:
            installer_profile: The installer profile instance
            
        Returns:
            QuerySet: Installations for the installer
        """
        return Installation.objects.filter(installer=installer_profile).order_by('-installation_created_date')
    
    @staticmethod
    def calculate_installer_stats(installations):
        """
        Calculate KPI statistics for an installer.
        
        Args:
            installations: QuerySet of installations
            
        Returns:
            dict: Statistics including total, in_progress, pending, completed, completion_rate
        """
        total_tasks = installations.count()
        in_progress = installations.filter(status='IN_PROGRESS').count()
        pending = installations.filter(status='PENDING_ACCEPTANCE').count()
        completed = installations.filter(status='COMPLETED').count()
        completion_rate = int((completed / total_tasks) * 100) if total_tasks > 0 else 0
        
        return {
            'total_tasks': total_tasks,
            'in_progress': in_progress,
            'pending': pending,
            'completed': completed,
            'completion_rate': completion_rate,
        }

