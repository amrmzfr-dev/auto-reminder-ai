from django.db import models
from django.conf import settings  # For referencing CustomUser
from ..models import InstallerProfile  # Replace with the actual path to your InstallerProfile model
from django.utils import timezone
from ..models import CustomUser

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
    """
    The central entity representing a single installation job.
    It acts as a state machine, tracking the job's entire lifecycle
    through the 'status' field.
    """
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('PENDING_ACCEPTANCE', 'Pending Acceptance'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('EXPIRED', 'Expired'),
    ]

    installation_id = models.CharField(
        max_length=50, unique=True, editable=False,
        help_text="Unique identifier for the installation job."
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='installations',
        help_text="The customer associated with this installation."
    )
    charger_model = models.ForeignKey(
        ChargerModel,
        on_delete=models.PROTECT,
        related_name='installations',
        help_text="The charger model to be installed."
    )
    assigned_installer = models.ForeignKey(
        CustomUser, # Link to your InstallerProfile model
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_installations_directly',
        help_text="The CustomUser id to bind directly for notifications."
    )
    installer = models.ForeignKey(
        InstallerProfile, # Link to your InstallerProfile model
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_installations',
        help_text="The installer assigned to this job. Can be null if unassigned."
    )

    installation_created_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date when the installation job was originally created."
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SUBMITTED', # Set default to 'SUBMITTED' as per documentation
        help_text="The current status of the installation job."
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Any additional notes or comments for the installation."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was first created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of the last update to the record."
    )
    assignment_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Crucial Field. Timestamp for when the installer's offer to accept expires. Null if not pending."
    )

    def save(self, *args, **kwargs):
        """
        Overrides the save method to generate installation_id based on customer's
        state and house_type, and set the creation date if not provided.
        """
        if not self.installation_id:
            # Generate installation_id based on customer's state and house_type
            state_code = self.customer.state[:2].upper()  # e.g., Selangor → 'SE'
            type_code = self.customer.house_type.upper()  # 'L' or 'H'

            # Count existing installations to get a sequential number
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
        """
        Returns a string representation of the installation job.
        """
        return f"Installation {self.installation_id} for {self.customer.name} ({self.get_status_display()})"

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
