from django import forms
from ..models import Customer, ChargerModel, Installation, ServiceLog, InstallerProfile
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()

# ----------------------------
# Combined form for Installation and Customer
# ----------------------------
class InstallationForm(forms.ModelForm):
    # Customer Fields
    customer_name = forms.CharField(max_length=200, label='Customer Name', widget=forms.TextInput(attrs={'class': 'form-control'}))
    contact_person = forms.CharField(max_length=100, required=False, label='Contact Person', widget=forms.TextInput(attrs={'class': 'form-control'}))
    customer_email = forms.EmailField(label='Customer Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=20, required=False, label='Phone Number', widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    state = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    postcode = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Installation
        # Exclude 'customer' as it will be created and assigned separately
        # 'created_at' and 'updated_at' are auto-populated
        exclude = ('customer', 'created_at', 'updated_at')
        
        widgets = {
            'installation_id': forms.TextInput(attrs={'class': 'form-control'}),
            'charger_model': forms.Select(attrs={'class': 'form-control'}),
            'installer': forms.Select(attrs={'class': 'form-control'}),
            'installation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actual_completion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_customer_email(self):
        email = self.cleaned_data.get('customer_email')
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError("A customer with this email already exists.")
        return email

    def save(self, commit=True):
        """
        Creates a new Customer instance and links it to the new Installation instance.
        """
        # Create a new Customer instance from the form data
        customer = Customer.objects.create(
            name=self.cleaned_data['customer_name'],
            contact_person=self.cleaned_data.get('contact_person'),
            email=self.cleaned_data['customer_email'],
            phone_number=self.cleaned_data.get('phone_number'),
            address=self.cleaned_data['address'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            postcode=self.cleaned_data['postcode'],
        )

        # Create the Installation instance
        # Use the parent save method but exclude customer-related fields
        installation = super().save(commit=False)
        installation.customer = customer  # Link the new customer
        if commit:
            installation.save()
            self.save_m2m()  # For many-to-many relationships (not used here, but good practice)
        
        return installation

# ----------------------------
# ServiceLogForm (no changes)
# ----------------------------
class ServiceLogForm(forms.ModelForm):
    class Meta:
        model = ServiceLog
        fields = '__all__'
        widgets = {
            'installation': forms.Select(attrs={'class': 'form-control'}),
            'service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'performed_by': forms.TextInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

# ----------------------------
# ChargerModelForm (no changes)
# ----------------------------
class ChargerModelForm(forms.ModelForm):
    class Meta:
        model = ChargerModel
        fields = '__all__'
        widgets = {
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control'}),
            'power_rating_kw': forms.NumberInput(attrs={'class': 'form-control'}),
            'connector_type': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }