from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# -----------------------------------------------
# 🔐 CUSTOM USER MODEL WITH ROLE-BASED ACCESS
# -----------------------------------------------

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('1', 'Admin'),
        ('2', 'Installer'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='2'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# -----------------------------------------------
# 🧾 INSTALLER PROFILE MODEL
# -----------------------------------------------

class InstallerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='installer_profile')

    # Essential fields for registration
    company_name = models.CharField("Registered Company Name", max_length=255)
    company_ssm_number = models.CharField("Company Registration Number (SSM)", max_length=50)
    operational_state = models.CharField(
        max_length=50,
        choices=[
            ('Central 1', 'Wilayah Persekutuan KL, Putrajaya'),
            ('Central 2', 'Selangor'),
            ('Northern', 'Perak, Kedah, Perlis, Penang'),
            ('Southern', 'N.Sembilan, Melaka, Johor'),
            ('East Coast', 'Pahang, Terengganu, Kelantan'),
            ('East Malaysia', 'Sabah, Sarawak'),
        ]
    )

    # PIC (Person in Charge)
    pic_name = models.CharField("PIC Name", max_length=255)
    pic_designation = models.CharField("PIC Designation", max_length=100)
    pic_contact_number = models.CharField("PIC Contact Number", max_length=15)

    # Deferred fields to be filled in profile later
    company_address = models.TextField("Business Address", blank=True)
    year_established = models.PositiveIntegerField(null=True, blank=True)
    epf_contributors = models.PositiveIntegerField(null=True, blank=True)

    # Regulatory and licensing (optional)
    is_st_registered = models.BooleanField(default=False)
    contractor_license_class = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], blank=True)
    is_cidb_registered = models.BooleanField(default=False)
    cidb_category = models.CharField(max_length=100, blank=True)
    cidb_grade = models.CharField(max_length=20, blank=True)
    is_sst_registered = models.BooleanField(default=False)
    sst_number = models.CharField(max_length=50, blank=True)
    has_insurance = models.BooleanField(default=False)
    has_coi_history = models.BooleanField(default=False)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name

# -----------------------------------------------
# 📋 TASK MANAGEMENT MODEL
# -----------------------------------------------

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
