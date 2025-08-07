# installer_forms.py
from django import forms
from ..models import CustomUser, InstallerProfile, State
from django.contrib.auth.forms import UserCreationForm

# A tuple of choices representing different state regions in Malaysia.
# This provides a human-readable name and a machine-readable key.
STATE_CHOICES = [
    ('Central 1', 'Central 1 (Wilayah Persekutuan Kuala Lumpur, Putrajaya)'),
    ('Central 2', 'Central 2 (Selangor)'),
    ('Northern', 'Northern (Perak, Kedah, Perlis, Pulau Pinang)'),
    ('Southern', 'Southern (N.Sembilan, Melaka, Johor)'),
    ('East Coast', 'East Coast (Pahang, Terengganu, Kelantan)'),
    ("East M'sia", "East M'sia (Sabah, Sarawak)"),
]

# Defines a form for contractor registration, inheriting from Django's UserCreationForm.
# This form is used to collect the initial user credentials and contractor-specific details
# needed to create a new user account and a basic profile.
class ContractorRegisterForm(UserCreationForm):
    # Field for the company's official name.
    company_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            # Tailwind CSS classes for styling the input field.
            'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600',
            'placeholder': 'Company Name'
        })
    )
    # Field for the full name of the Person in Charge (PIC).
    pic_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600',
            'placeholder': 'PIC Full Name'
        })
    )
    # Field for the PIC's email address, a required field.
    pic_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600',
            'placeholder': 'PIC Email'
        })
    )
    # Field for the PIC's contact number.
    pic_contact_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600',
            'placeholder': 'PIC Contact Number'
        })
    )
    # Checkbox for agreeing to terms and conditions. It's required for submission.
    agree_terms = forms.BooleanField(
        required=True,
        label="I agree to the terms and conditions",
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-gray-600 text-indigo-600 focus:ring-indigo-500'
        })
    )

    # Overrides the default password fields from UserCreationForm to apply custom styling.
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600',
            'placeholder': 'Password'
        })
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        # Specifies the model this form is for, which is the CustomUser model.
        model = CustomUser
        # Defines the fields from the CustomUser model to be used in this form.
        # Note: The additional fields like `company_name`, `pic_name`, etc.,
        # are handled separately in the form's `save()` method.
        fields = ['username', 'password1', 'password2']
        # Customizes the widget for the username field with styling and a placeholder.
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600',
                'placeholder': 'Username'
            })
        }

# Imports forms and models, ensuring correct pathing for `InstallerProfile`.
# from django import forms
# from .models import InstallerProfile, State

# Defines a form for managing an installer's detailed profile.
# This form is based on the `InstallerProfile` model and is used to
# update or complete a contractor's profile after initial registration.
class InstallerProfileForm(forms.ModelForm):
    # A ModelMultipleChoiceField to select multiple operational states.
    # The queryset fetches all available `State` objects.
    # The widget uses checkboxes for multi-selection.
    operational_states = forms.ModelMultipleChoiceField(
        queryset=State.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Operational States',
        required=False
    )

    # The `__init__` method is overridden to apply custom styling to specific fields
    # dynamically when the form is initialized.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # List of boolean fields that will be styled as toggle switches.
        # A custom CSS class `sr-only peer` is applied to hide the default
        # checkbox while allowing a styled label to control it via CSS.
        checkbox_fields = [
            'is_st_registered', 'is_cidb_registered', 'is_sst_registered',
            'plwc_has_insurance', 'coi_history'
        ]
        for field_name in checkbox_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'class': 'sr-only peer'
                })

        # List of file input fields. These are hidden to use a custom-styled button/label
        # for file selection instead of the default browser file input.
        file_fields = [
            'st_certificate', 'cidb_certificate', 'sst_certificate',
            'insurance_certificate', 'coi_certificate'
        ]
        for field_name in file_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'class': 'custom-file-input',
                    'hidden': True
                })

    class Meta:
        # The model this form is associated with.
        model = InstallerProfile
        # Fields to exclude from the form. These are typically managed automatically.
        exclude = ['user', 'created_at', 'registration_status']
        # Custom labels for the form fields, providing more descriptive text
        # for the user interface.
        labels = {
            'is_st_registered': 'ST Registered',
            'license_class': 'Contractor License Class',
            'st_certificate': 'ST Certification (PDF)',

            'is_cidb_registered': 'CIDB Registered',
            'cidb_grade': 'CIDB Grade',
            'cidb_category': 'CIDB Category',
            'cidb_certificate': 'CIDB Certificate (PDF)',

            'is_sst_registered': 'SST Registered',
            'sst_number': 'SST Number',
            'sst_certificate': 'SST Certificate (PDF)',

            'plwc_has_insurance': 'Has Insurance',
            'insurance_certificate': 'PLWC Insurance Certificate (PDF)',

            'coi_history': 'Has COI History',
            'coi_certificate': 'COI Certificate (PDF)',
        }
        # Custom widget definitions for various fields. This is used to apply
        # specific CSS classes for styling and control the input type (e.g., Textarea).
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'w-9/12 bg-gray-700 text-white rounded-md p-3 border border-gray-600'}),
            'company_ssm_number': forms.TextInput(attrs={'class': 'w-9/12 bg-gray-700 text-white rounded-md p-3 border border-gray-600'}),
            'year_established': forms.NumberInput(attrs={'class': 'w-9/12 bg-gray-700 text-white rounded-md p-3 border border-gray-600'}),
            'epf_contributors': forms.NumberInput(attrs={'class': 'w-9/12 bg-gray-700 text-white rounded-md p-3 border border-gray-600'}),
            'company_address': forms.Textarea(attrs={'rows': 3, 'class': 'w-9/12 bg-gray-700 text-white rounded-md p-3 border border-gray-600'}),

            'pic_name': forms.TextInput(attrs={'class': 'w-9/12 bg-gray-700 text-white rounded-md p-3 border border-gray-600'}),
            'pic_designation': forms.TextInput(attrs={'class': 'w-9/12 bg-gray-700 text-white rounded-md p-3 border border-gray-600'}),
            'pic_contact_number': forms.TextInput(attrs={'class': 'w-9/12 bg-gray-700 text-white rounded-md p-3 border border-gray-600'}),
            'pic_email': forms.EmailInput(attrs={'class': 'w-9/12 bg-gray-700 text-white rounded-md p-3 border border-gray-600'}),

            'license_class': forms.Select(attrs={'class': 'w-9/12 bg-gray-700 text-white rounded-md p-3 border border-gray-600'}),
            'cidb_grade': forms.Select(attrs={'class': 'w-9/12 bg-gray-700 text-white rounded-md p-3 border border-gray-600'}),
            'cidb_category': forms.Select(attrs={'class': 'w-9/12 bg-gray-700 text-white rounded-md p-3 border border-gray-600'}),
            'sst_number': forms.TextInput(attrs={'class': 'w-9/12 bg-gray-700 text-white rounded-md p-3 border border-gray-600'}),
        }

    # The `clean()` method is overridden to add custom validation logic.
    # This ensures that if a user checks a registration box (e.g., 'ST Registered'),
    # they must also provide the corresponding certificate file.
    def clean(self):
        # Calls the parent class's clean() method to perform initial validation.
        cleaned_data = super().clean()

        # A list of tuples, where each tuple links a boolean toggle field
        # to its corresponding file field and a human-readable label.
        conditional_requirements = [
            ('is_st_registered', 'st_certificate', 'ST Certificate'),
            ('is_cidb_registered', 'cidb_certificate', 'CIDB Certificate'),
            ('is_sst_registered', 'sst_certificate', 'SST Certificate'),
            ('plwc_has_insurance', 'insurance_certificate', 'Insurance Certificate'),
            ('coi_history', 'coi_certificate', 'COI Certificate'),
        ]

        # Iterates through the list to check the conditional dependencies.
        for toggle_field, file_field, label in conditional_requirements:
            toggle = cleaned_data.get(toggle_field)
            file = cleaned_data.get(file_field)

            # If the toggle is checked (`True`) but no file is provided,
            # an error is added to the form for that specific file field.
            if toggle and not file:
                self.add_error(file_field, f"{label} is required when '{self.fields[toggle_field].label}' is checked.")

        # Returns the cleaned data, which now includes the custom validation errors if any.
        return cleaned_data