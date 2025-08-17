from django import forms
from ..models import Customer, ChargerModel, Installation, ServiceLog, InstallerProfile, CustomUser
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()

# ----------------------------
# Combined form for Installation and Customer
# ----------------------------
from django import forms
from accounts.models import Installation, Customer, ChargerModel, InstallerProfile

class InstallationForm(forms.ModelForm):
    """
    Form for creating a new Installation job,
    and simultaneously creating its associated Customer record.
    """
    # Customer Fields - These are NOT part of Installation model, but created in form's save()
    customer_name = forms.CharField(max_length=200, label='Customer Name')
    contact_person = forms.CharField(max_length=100, required=False, label='Contact Person')
    customer_email = forms.EmailField(label='Customer Email')
    phone_number = forms.CharField(max_length=20, required=False, label='Phone Number')
    address = forms.CharField(widget=forms.Textarea(), label='Address')
    city = forms.CharField(max_length=100, label='City')
    state = forms.ChoiceField(
        choices=Customer.STATE_CHOICES,
        label='State',
        widget=forms.Select(attrs={
            'class': 'w-9/12 bg-[#222222] text-white text-sm rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none'
        })
    )

    house_type = forms.ChoiceField(
        choices=Customer.HOUSE_TYPE_CHOICES,
        label='House Type',
        widget=forms.Select(attrs={
            'class': 'w-9/12 bg-[#222222] text-white text-sm rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none'
        })
    )
    postcode = forms.CharField(max_length=10, label='Postcode')

    # Installation Fields (Directly from Installation model)
    charger_model = forms.ModelChoiceField(
        queryset=ChargerModel.objects.all(),
        empty_label='Choose Charger Model',
        label='Charger Model',
        widget=forms.Select(attrs={'class': 'w-9/12 bg-[#222222] text-white text-sm rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none'}),
    )
    
    # Installer dropdown (optional) - InstallerProfile ForeignKey on Installation
    installer = forms.ModelChoiceField(
        queryset=InstallerProfile.objects.all(),
        required=False, # This is correctly set to False here
        empty_label='Choose Installer Company (Optional)',
        label='Installer Company',
        widget=forms.Select(attrs={'class': 'w-9/12 bg-[#222222] text-white text-sm rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none'}),
    )

    # Assigned Installer (CustomUser) - AssignedInstaller ForeignKey on Installation
    # This field is crucial for the notification system as it links to CustomUser
    assigned_installer = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='2').order_by('username'), # Filter for installer users
        required=False, # This is also optional at creation
        empty_label="Choose Installer User (Optional)",
        label="Assign Installer User Account",
        widget=forms.Select(attrs={'class': 'w-9/12 bg-[#222222] text-white text-sm rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply common classes to all fields
        common_input_classes = 'w-9/12 bg-[#222222] text-white text-sm rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none'
        for field_name, field in self.fields.items():
            # Apply styling to all fields
            if field_name not in ['state', 'house_type', 'charger_model', 'installer', 'assigned_installer']:
                field.widget.attrs.update({'class': common_input_classes})
            
            # Textarea specific rows
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 4

            # Explicitly set required status based on individual field definitions
            # This ensures required=False on fields like contact_person, phone_number, installer, assigned_installer is respected.
            if field_name in ['contact_person', 'phone_number', 'notes']:
                field.required = False # Override if __init__ somehow set it to True
            elif field_name == 'installer' or field_name == 'assigned_installer':
                field.required = False
            # For all other fields, default required=True (which is usually their default anyway)

    def clean_state(self):
        state = self.cleaned_data.get('state')
        if not state:
            raise forms.ValidationError("Please select a state.")
        return state

    def clean_customer_email(self):
        return self.cleaned_data.get('customer_email')


    def clean(self):
        cleaned_data = super().clean()
        assigned_installer = cleaned_data.get('assigned_installer')
        installer_profile = cleaned_data.get('installer')

        # Custom validation to ensure a selected profile is linked to the assigned user
        if assigned_installer and installer_profile:
            if installer_profile.user != assigned_installer:
                self.add_error('installer', "The selected installer company profile must be linked to the assigned user account.")
                self.add_error('assigned_installer', "The selected user account must be linked to the assigned installer company profile.")
        
        # If an installer profile is selected, but no user, ensure the profile has a user
        if installer_profile and not assigned_installer:
            if not installer_profile.user:
                self.add_error('installer', "The selected installer company profile does not have an associated user account. Please select a user or a profile with a linked user.")
        
        # Ensure that if a user is assigned, they are actually an installer role
        if assigned_installer and assigned_installer.role != '2': # Assuming '2' is Installer role
            self.add_error('assigned_installer', "The assigned user must have the 'Installer' role.")

        return cleaned_data

    class Meta:
        model = Installation
        # 'fields' explicitly lists all fields that the form should handle.
        # 'status', 'installation_id', 'created_at', 'updated_at', 'assignment_expires_at',
        # and 'installation_created_date' are handled programmatically in the view
        # or by model defaults/auto_now, so they are not in the form.
        fields = [
            'customer_name', 'contact_person', 'customer_email', 'phone_number',
            'address', 'city', 'state', 'house_type', 'postcode',
            'charger_model', 'installer', 'assigned_installer', 'notes'
        ]
        # Widgets are already defined for most fields above or will inherit from default
        # No need for a separate widgets dict here unless overriding for fields not listed above.

    def save(self, commit=True):
        print("[DEBUG] Starting form save()...")
        
        # Create Customer instance from form data
        customer_data = {
            'name': self.cleaned_data['customer_name'],
            'contact_person': self.cleaned_data.get('contact_person'),
            'email': self.cleaned_data['customer_email'],
            'phone_number': self.cleaned_data.get('phone_number'),
            'address': self.cleaned_data['address'],
            'city': self.cleaned_data['city'],
            'state': self.cleaned_data['state'],
            'house_type': self.cleaned_data['house_type'],
            'postcode': self.cleaned_data['postcode'],
        }
        # Check if customer already exists by email, if so, retrieve instead of create
        customer, created = Customer.objects.get_or_create(
            email=customer_data['email'],
            defaults=customer_data
        )
        if not created:
            # If customer exists, update existing fields from form (optional, depending on desired behavior)
            for key, value in customer_data.items():
                setattr(customer, key, value)
            customer.save()
            print(f"[DEBUG] Existing Customer retrieved/updated: {customer}")
        else:
            print(f"[DEBUG] New Customer created: {customer}")

        # Create Installation instance from form data
        installation = super().save(commit=False) # Get the Installation instance without saving yet
        installation.customer = customer # Link the created/retrieved Customer

        # Fields that are directly on Installation and need to be set
        installation.charger_model = self.cleaned_data['charger_model']
        installation.notes = self.cleaned_data.get('notes')
        installation.customer_name = self.cleaned_data['customer_name'] # Re-set from form
        installation.customer_email = self.cleaned_data['customer_email'] # Re-set from form
        installation.address = self.cleaned_data['address'] # Re-set from form

        # Installer assignment (CustomUser and InstallerProfile)
        installation.assigned_installer = self.cleaned_data.get('assigned_installer')
        installation.installer = self.cleaned_data.get('installer')

        # Status and expiration will be handled in the view where this form is used (e.g., create_installation_view)
        # This form's save method focuses on saving the basic Installation and Customer data.

        if commit:
            installation.save()
            # If your Installation model had ManyToMany fields (it doesn't appear to), you'd call self.save_m2m() here
            print(f"[DEBUG] Installation saved (ID: {installation.installation_id})")

        return installation

# ----------------------------
# ServiceLogForm (changes applied)
# ----------------------------
class ServiceLogForm(forms.ModelForm):
    class Meta:
        model = ServiceLog
        fields = '__all__'
        widgets = {
            'installation': forms.Select(attrs={'class': 'bg-[#222222] text-white rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none'}),
            'service_date': forms.DateInput(attrs={'class': 'bg-[#222222] text-white rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'bg-[#222222] text-white rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none', 'rows': 4}),
            'performed_by': forms.TextInput(attrs={'class': 'bg-[#222222] text-white rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none'}),
            'cost': forms.NumberInput(attrs={'class': 'bg-[#222222] text-white rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none'}),
            'notes': forms.Textarea(attrs={'class': 'bg-[#222222] text-white rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none', 'rows': 4}),
        }

# ----------------------------
# ChargerModelForm (changes applied)
# ----------------------------
class ChargerModelForm(forms.ModelForm):
    class Meta:
        model = ChargerModel
        fields = '__all__'
        widgets = {
            'manufacturer': forms.TextInput(attrs={'class': 'bg-[#222222] text-white rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none'}),
            'model_name': forms.TextInput(attrs={'class': 'bg-[#222222] text-white rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none'}),
            'power_rating_kw': forms.NumberInput(attrs={'class': 'bg-[#222222] text-white rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none'}),
            'connector_type': forms.TextInput(attrs={'class': 'bg-[#222222] text-white rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none'}),
            'description': forms.Textarea(attrs={'class': 'bg-[#222222] text-white rounded-md p-3 border border-[#2c2c2c] focus:ring-0 focus:border-[#2c2c2c] focus:outline-none', 'rows': 4}),
        }