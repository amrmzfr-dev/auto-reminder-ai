from django.db import models
from django.conf import settings  # For referencing CustomUser
from models import InstallerProfile  # Replace with the actual path to your InstallerProfile model

# ----------------------------
# Customer
# ----------------------------
class Customer(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postcode = models.CharField(max_length=10)

    def __str__(self):
        return self.name

# ----------------------------
# ChargerModel
# ----------------------------
class ChargerModel(models.Model):
    manufacturer = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100, unique=True)
    power_rating_kw = models.DecimalField(max_digits=5, decimal_places=2)
    connector_type = models.CharField(max_length=50, help_text="e.g., Type 2, CCS, CHAdeMO")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.manufacturer} {self.model_name} ({self.power_rating_kw} kW)"

# ----------------------------
# Installation
# ----------------------------
class Installation(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('On Hold', 'On Hold'),
    ]

    installation_id = models.CharField(
        max_length=50, unique=True, help_text="Unique identifier for the installation"
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='installations')
    charger_model = models.ForeignKey(ChargerModel, on_delete=models.PROTECT, related_name='installations')

    installer = models.ForeignKey(
        InstallerProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_installations'
    )

    installation_date = models.DateField()
    actual_completion_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    notes = models.TextField(blank=True, null=True)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='my_installations'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Installation {self.installation_id} for {self.customer.name} ({self.status})"

# ----------------------------
# ServiceLog
# ----------------------------
class ServiceLog(models.Model):
    installation = models.ForeignKey(Installation, on_delete=models.CASCADE, related_name='service_logs')
    service_date = models.DateField()
    description = models.TextField()
    performed_by = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Name of installer or internal staff who performed the service"
    )
    cost = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Service for {self.installation.installation_id} on {self.service_date}"
