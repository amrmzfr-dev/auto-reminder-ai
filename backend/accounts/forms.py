from django import forms
from .models import Task, CustomUser, InstallerProfile, State
from django.contrib.auth.forms import UserCreationForm

STATE_CHOICES = [
    ('Central 1', 'Central 1 (Wilayah Persekutuan Kuala Lumpur, Putrajaya)'),
    ('Central 2', 'Central 2 (Selangor)'),
    ('Northern', 'Northern (Perak, Kedah, Perlis, Pulau Pinang)'),
    ('Southern', 'Southern (N.Sembilan, Melaka, Johor)'),
    ('East Coast', 'East Coast (Pahang, Terengganu, Kelantan)'),
    ("East M'sia", "East M'sia (Sabah, Sarawak)"),
]

class AdminRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = '1'  # Force admin role
        if commit:
            user.save()
        return user

class ContractorRegisterForm(UserCreationForm):
    company_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600',
            'placeholder': 'Company Name'
        })
    )
    pic_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600',
            'placeholder': 'PIC Full Name'
        })
    )
    pic_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600',
            'placeholder': 'PIC Email'
        })
    )
    pic_contact_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600',
            'placeholder': 'PIC Contact Number'
        })
    )
    agree_terms = forms.BooleanField(
        required=True,
        label="I agree to the terms and conditions",
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-gray-600 text-indigo-600 focus:ring-indigo-500'
        })
    )

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
        model = CustomUser
        fields = ['username', 'password1', 'password2']  # Only fields in CustomUser
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600',
                'placeholder': 'Username'
            })
        }

from django import forms
from .models import InstallerProfile

class InstallerProfileForm(forms.ModelForm):
    operational_states = forms.ModelMultipleChoiceField(
        queryset=State.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Operational States',
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Boolean fields: toggle switch styling
        checkbox_fields = [
            'is_st_registered', 'is_cidb_registered', 'is_sst_registered',
            'plwc_has_insurance', 'coi_history'
        ]
        for field_name in checkbox_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'class': 'sr-only peer'
                })

        # File input fields: hidden + custom file input class
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
        model = InstallerProfile
        exclude = ['user', 'created_at', 'registration_status']
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

    def clean(self):
        cleaned_data = super().clean()

        conditional_requirements = [
            ('is_st_registered', 'st_certificate', 'ST Certificate'),
            ('is_cidb_registered', 'cidb_certificate', 'CIDB Certificate'),
            ('is_sst_registered', 'sst_certificate', 'SST Certificate'),
            ('plwc_has_insurance', 'insurance_certificate', 'Insurance Certificate'),
            ('coi_history', 'coi_certificate', 'COI Certificate'),
        ]

        for toggle_field, file_field, label in conditional_requirements:
            toggle = cleaned_data.get(toggle_field)
            file = cleaned_data.get(file_field)

            if toggle and not file:
                self.add_error(file_field, f"{label} is required when '{self.fields[toggle_field].label}' is checked.")

        return cleaned_data

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['due_date']  # Exclude due_date from form
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600',
                'placeholder': 'Enter task title'
            }),
            'pic': forms.TextInput(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600',
                'placeholder': 'Person in charge'
            }),
            'document': forms.ClearableFileInput(attrs={
                'class': (
                    'block w-full text-sm text-white bg-gray-700 border border-gray-600 '
                    'rounded-md cursor-pointer p-3 file:mr-4 file:py-2 file:px-4 '
                    'file:rounded-md file:border-0 file:text-sm file:font-semibold '
                    'file:bg-indigo-600 file:text-white hover:file:bg-indigo-700'
                )
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600 resize-none',
                'rows': 4,
                'placeholder': 'Additional notes or remarks'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600'
            }),
        }