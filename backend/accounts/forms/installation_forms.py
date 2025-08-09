from django import forms
from ..models import Customer, ChargerModel, Installation, ServiceLog, InstallerProfile
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()

# ----------------------------
# Combined form for Installation and Customer
# ----------------------------
from django import forms
from accounts.models import Installation, Customer, ChargerModel, InstallerProfile

class InstallationForm(forms.ModelForm):
    # Customer Fields
    customer_name = forms.CharField(max_length=200, label='Customer Name')
    contact_person = forms.CharField(max_length=100, required=False, label='Contact Person')
    customer_email = forms.EmailField(label='Customer Email')
    phone_number = forms.CharField(max_length=20, required=False, label='Phone Number')
    address = forms.CharField(widget=forms.Textarea())
    city = forms.CharField(max_length=100)

    # State dropdown
    state = forms.ChoiceField(
        choices=Customer.STATE_CHOICES,
        label='State'
    )

    def clean_state(self):
        state = self.cleaned_data.get('state')
        if not state:
            raise forms.ValidationError("Please select a state.")
        return state

    # House Type dropdown
    house_type = forms.ChoiceField(
        choices=Customer.HOUSE_TYPE_CHOICES,
        label='House Type'
    )

    postcode = forms.CharField(max_length=10)

    # Charger dropdown
    charger_model = forms.ModelChoiceField(
        queryset=ChargerModel.objects.all(),
        empty_label='Choose Charger Model',
        label='Charger Model'
    )
    
    # Installer dropdown (optional)
    installer = forms.ModelChoiceField(
        queryset=InstallerProfile.objects.all(),
        required=False,
        empty_label='Choose Installer',
        label='Installer'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make all fields required by default except installer
        for field_name, field in self.fields.items():
            if field_name == 'installer':
                field.required = False
            else:
                field.required = True

        # 'notes' optional
        if 'notes' in self.fields:
            self.fields['notes'].required = False

        common_input_classes = 'w-9/12 bg-gray-700 text-white rounded-md p-3 border border-gray-600'

        customer_fields = [
            'customer_name', 'contact_person', 'customer_email',
            'phone_number', 'address', 'city', 'state', 'house_type', 'postcode'
        ]
        for field_name in customer_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'class': common_input_classes})
                if field_name == 'address' and isinstance(self.fields[field_name].widget, forms.Textarea):
                    self.fields[field_name].widget.attrs['rows'] = 4

        installation_fields = [
            'charger_model', 'installer', 'notes'
        ]
        for field_name in installation_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'class': common_input_classes})
                if field_name == 'notes' and isinstance(self.fields[field_name].widget, forms.Textarea):
                    self.fields[field_name].widget.attrs['rows'] = 4

    class Meta:
        model = Installation
        exclude = (
            'customer', 'created_at', 'updated_at', 'installation_created_date', 'status'
        )
        widgets = {}

    def clean_customer_email(self):
        email = self.cleaned_data.get('customer_email')
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError("A customer with this email already exists.")
        return email

    def save(self, commit=True):
        print("[DEBUG] Starting form save()...")
        customer = Customer.objects.create(
            name=self.cleaned_data['customer_name'],
            contact_person=self.cleaned_data.get('contact_person'),
            email=self.cleaned_data['customer_email'],
            phone_number=self.cleaned_data.get('phone_number'),
            address=self.cleaned_data['address'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            house_type=self.cleaned_data['house_type'],
            postcode=self.cleaned_data['postcode'],
        )
        print(f"[DEBUG] Customer created: {customer}")

        installation = super().save(commit=False)
        installation.customer = customer
        installation.charger_model = self.cleaned_data['charger_model']
        installation.installer = self.cleaned_data.get('installer')  # Set installer if provided

        if commit:
            installation.save()
            self.save_m2m()
            print(f"[DEBUG] Installation created: {installation}")

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
