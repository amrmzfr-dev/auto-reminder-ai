from django.db import models
from django.conf import settings  # For referencing CustomUser
from ..models import InstallerProfile  # Replace with the actual path to your InstallerProfile model
from django.utils import timezone

# ----------------------------
# Customer
# ----------------------------
class Customer(models.Model):
    # State codes for Malaysia
    STATE_CHOICES = [
    ('', 'Choose State'),  # Placeholder
    ('Johor', 'Johor'),
    ('Kedah', 'Kedah'),
    ('Kelantan', 'Kelantan'),
    ('Melaka', 'Melaka'),
    ('Negeri Sembilan', 'Negeri Sembilan'),
    ('Pahang', 'Pahang'),
    ('Penang', 'Penang'),
    ('Perak', 'Perak'),
    ('Perlis', 'Perlis'),
    ('Sabah', 'Sabah'),
    ('Sarawak', 'Sarawak'),
    ('Selangor', 'Selangor'),
    ('Terengganu', 'Terengganu'),
    ('Kuala Lumpur', 'Kuala Lumpur'),
    ('Labuan', 'Labuan'),
    ('Putrajaya', 'Putrajaya'),
]

    # Property type codes
    HOUSE_TYPE_CHOICES = [
        ('L', 'Landed House'),
        ('H', 'High-Rise'),
    ]

    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, blank=True)
    house_type = models.CharField(max_length=1, choices=HOUSE_TYPE_CHOICES, default='L')  # L or H
    postcode = models.CharField(max_length=10)

    def __str__(self):
        return self.name

# ----------------------------
# ChargerModel
# ----------------------------
class ChargerModel(models.Model):
    # Predefined charger model choices (Manufacturer + Model)
    CHARGER_MODEL_CHOICES = [
        ('ABB Terra AC 22', 'ABB Terra AC 22'),
        ('ABB Terra DC 50', 'ABB Terra DC 50'),
        ('Delta DC Wallbox 25', 'Delta DC Wallbox 25'),
        ('Schneider EVlink AC 22', 'Schneider EVlink AC 22'),
        ('Siemens VersiCharge 22', 'Siemens VersiCharge 22'),
        ('Tesla Wall Connector Gen 3', 'Tesla Wall Connector Gen 3'),
    ]

    manufacturer = models.CharField(max_length=100)
    model_name = models.CharField(
        max_length=100,
        choices=CHARGER_MODEL_CHOICES,
        help_text="Select the charger model"
    )
    power_rating_kw = models.DecimalField(max_digits=5, decimal_places=2)
    connector_type = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.model_name} ({self.power_rating_kw} kW)"

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
        max_length=50, unique=True, editable=False
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

    installation_created_date = models.DateField(null=True, blank=True)  # allow blank/null

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.installation_id:
            state_code = self.customer.state[:2].upper()  # e.g., Selangor → 'SE'
            type_code = self.customer.house_type.upper()  # 'L' or 'H'

            count = Installation.objects.filter(
                customer__state=self.customer.state,
                customer__house_type=self.customer.house_type
            ).count() + 1

            self.installation_id = f"{state_code}{type_code}{count:06d}"

        # Set default date if not provided
        if not self.installation_created_date:
            self.installation_created_date = timezone.now().date()

        super().save(*args, **kwargs)

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
