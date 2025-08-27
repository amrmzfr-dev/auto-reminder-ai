# notifications/models.py
from django.db import models
from django.contrib.auth.models import User # Assuming Django's built-in User model
from ..models import Installation # Assuming your Installation model is in an 'installations' app
from ..models import CustomUser
from .admin_models import Task

class Notification(models.Model):
    """
    Represents an individual notification message for a user within the system.
    This model powers the in-app notification system.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="The user who will receive this notification."
    )
    message = models.TextField(
        help_text="The content of the notification message (e.g., 'Installer John Doe has accepted the job.')."
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Tracks if the user has viewed this notification. Defaults to False."
    )
    related_installation = models.ForeignKey(
        Installation,
        on_delete=models.SET_NULL, # If an installation is deleted, don't delete the notification
        null=True,
        blank=True,
        related_name='notifications',
        help_text="An optional link to the relevant installation, allowing clicks to navigate directly to the job details."
    )
    related_task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL, # If a task is deleted, don't delete the notification
        null=True,
        blank=True,
        related_name='notifications',
        help_text="An optional link to the relevant task, allowing clicks to navigate directly to the task details."
    )
    # Optional priority display for task-related notifications
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        null=True,
        blank=True,
        help_text="Optional priority for the related task (High/Medium/Low)."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the notification was created."
    )

    class Meta:
        # Orders notifications by creation date, most recent first
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        """
        Returns a string representation of the notification, useful for Django admin.
        """
        read_status = "Read" if self.is_read else "Unread"
        return f"Notification for {self.user.username} ({read_status}): {self.message[:50]}..."

    def mark_as_read(self):
        """
        Helper method to mark a notification as read.
        """
        if not self.is_read:
            self.is_read = True
            self.save()

    def get_related_url(self):
        """
        Returns a URL for the related installation or task, if any.
        This allows clicks to navigate directly to the relevant details.
        """
        if self.related_installation:
            return f"/auth/{self.related_installation.installation_id}/"
        elif self.related_task:
            return f"/auth/task/{self.related_task.pk}/"
        return "#" # Return a generic link if no related item
