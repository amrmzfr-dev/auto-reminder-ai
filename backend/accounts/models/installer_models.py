import os
import re
from django.db import models
from django.contrib.auth.models import AbstractUser
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


def upload_to_cert(instance, filename):
    # Normalize company name for folder and filename
    company_name = re.sub(r'[^A-Za-z0-9]+', '-', instance.company_name.upper()).strip('-')

    # Map fields to suffix labels
    field_suffix_mapping = {
        'st_certificate': 'ST-CERTIFICATE',
        'cidb_certificate': 'CIDB-CERTIFICATE',
        'sst_certificate': 'SST-CERTIFICATE',
        'insurance_certificate': 'INSURANCE-CERTIFICATE',
        'coi_certificate' : 'COI-CERTIFICATE',
    }

    suffix = None
    for field, suffix_label in field_suffix_mapping.items():
        file_field = getattr(instance, field)
        if file_field and file_field.name == filename:
            suffix = suffix_label
            break

    ext = os.path.splitext(filename)[1]
    new_filename = f"{company_name}_{suffix}{ext}" if suffix else filename

    # Store all certs under a single company folder
    return f"certificates/{company_name}/{new_filename}"

class State(models.Model):
    code = models.CharField(max_length=20, unique=True)  # e.g., "Central 1"
    name = models.CharField(max_length=100)  # e.g., "Central 1 (Wilayah Persekutuan Kuala Lumpur, Putrajaya)"

    def __str__(self):
        return self.name

STATUS_CHOICES = [
    ('incomplete', 'Incomplete'),
    ('submitted', 'Submitted'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

STATE_CHOICES = [
    ('Central 1', 'Central 1 (Wilayah Persekutuan Kuala Lumpur, Putrajaya)'),
    ('Central 2', 'Central 2 (Selangor)'),
    ('Northern', 'Northern (Perak, Kedah, Perlis, Pulau Pinang)'),
    ('Southern', 'Southern (N.Sembilan, Melaka, Johor)'),
    ('East Coast', 'East Coast (Pahang, Terengganu, Kelantan)'),
    ("East M'sia", "East M'sia (Sabah, Sarawak)"),
]

LICENSE_CLASS_CHOICES = [
    ('A', 'Class A'),
    ('B', 'Class B'),
    ('C', 'Class C'),
]

CIDB_CATEGORY_CHOICES = [
    ('B', 'B (Building)'),
    ('CE', 'CE (Civil Engineering)'),
    ('ME', 'ME (Mechanical & Electrical)'),
]

CIDB_GRADE_CHOICES = [
    ('G1', 'G1'), ('G2', 'G2'), ('G3', 'G3'), ('G4', 'G4'),
    ('G5', 'G5'), ('G6', 'G6'), ('G7', 'G7'),
]

class InstallerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True, help_text="The CustomUser account associated with this installer" \
    "profile.")

    # Basic company and PIC details
    company_name = models.CharField(max_length=255, null=True, blank=True)
    company_ssm_number = models.CharField(max_length=100, null=True, blank=True)
    operational_states = models.ManyToManyField(State, blank=True)
    company_address = models.TextField(null=True, blank=True)
    year_established = models.PositiveIntegerField(null=True, blank=True)
    epf_contributors = models.PositiveIntegerField(null=True, blank=True)

    pic_name = models.CharField(max_length=255, null=True, blank=True)
    pic_designation = models.CharField(max_length=100, null=True, blank=True)
    pic_contact_number = models.CharField(max_length=20, null=True, blank=True)
    pic_email = models.EmailField(null=True, blank=True)

    # Compliance and certification
    # ST Registration
    is_st_registered = models.BooleanField(default=False)
    license_class = models.CharField(max_length=10, choices=LICENSE_CLASS_CHOICES, null=True, blank=True)
    st_certificate = models.FileField(upload_to=upload_to_cert, null=True, blank=True)

    # CIDB Registration
    is_cidb_registered = models.BooleanField(default=False)
    cidb_category = models.CharField(max_length=100, choices=CIDB_CATEGORY_CHOICES, null=True, blank=True)
    cidb_grade = models.CharField(max_length=10, choices=CIDB_GRADE_CHOICES, null=True, blank=True)
    cidb_certificate = models.FileField(upload_to=upload_to_cert, null=True, blank=True)

    # SST Registration
    is_sst_registered = models.BooleanField(default=False)
    sst_number = models.CharField(max_length=100, null=True, blank=True)
    sst_certificate = models.FileField(upload_to=upload_to_cert, null=True, blank=True)

    # Insurance (PLWC)
    plwc_has_insurance = models.BooleanField(default=False)
    insurance_certificate = models.FileField(upload_to=upload_to_cert, null=True, blank=True)

    # Inspection COI for EVCS
    coi_history = models.BooleanField(default=False)
    coi_certificate = models.FileField(upload_to=upload_to_cert, null=True, blank=True)

    # Status & timestamps
    registration_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='incomplete'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Required fields for submission
        required_fields = [
            self.company_name,
            self.pic_name,
            self.pic_contact_number,
            self.pic_email,
            self.company_ssm_number,
            self.pic_designation,
            self.company_address,
            self.year_established,
            self.epf_contributors,
        ]

        # If all required fields are filled and status is still incomplete
        if all(required_fields) and self.registration_status == 'incomplete':
            self.registration_status = 'submitted'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company_name or 'Unnamed Installer Profile'}"
    

