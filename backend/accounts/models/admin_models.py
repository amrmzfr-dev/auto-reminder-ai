from django.db import models

class Task(models.Model):
    # Priority levels for task urgency
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    # Status stages in task lifecycle
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    # Task metadata
    title = models.CharField(max_length=255)
    pic = models.CharField(max_length=100)  # Person in charge
    document = models.FileField(upload_to='tasks/docs/', blank=True, null=True)
    remarks = models.TextField(blank=True)

    # System-generated fields
    created_at = models.DateTimeField(auto_now_add=True)

    # Task attributes
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return self.title
