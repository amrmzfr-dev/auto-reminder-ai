from django import forms
from .models import Task
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, InstallerProfile

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
            'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600',
            'placeholder': 'Company Name'
        })
    )
    pic_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600',
            'placeholder': 'PIC Full Name'
        })
    )
    pic_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600',
            'placeholder': 'PIC Email'
        })
    )
    pic_contact_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600',
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
            'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600',
            'placeholder': 'Password'
        })
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']  # Only fields in CustomUser
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600',
                'placeholder': 'Username'
            })
        }

class InstallerProfileForm(forms.ModelForm):
    class Meta:
        model = InstallerProfile
        exclude = ['user', 'created_at', 'registration_status']

        labels = {
            'is_st_registered': 'Is ST Registered',
            'company_name': 'Company Name',
            'company_ssm_number': 'Company SSM Number',
            'operational_state': 'Operational State',
            'year_established': 'Year Established',
            'epf_contributors': 'EPF Contributors',
            'company_address': 'Company Address',
            'pic_name': 'PIC Name',
            'pic_designation': 'PIC Designation',
            'pic_contact_number': 'PIC Contact Number',
            'pic_email': 'PIC Email',
            'contractor_license_class': 'Contractor License Class',
            'cidb_grade': 'CIDB Grade',
            'cidb_category': 'CIDB Category',
            'sst_number': 'SST Number',
            'is_sst_registered': 'Is SST Registered',
            'is_cidb_registered': 'Is CIDB Registered',
            'is_registered': 'Is Registered',
            'has_insurance': 'Has Insurance',
            'has_coi_history': 'Has COI History',
        }

        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'}),
            'company_ssm_number': forms.TextInput(attrs={'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'}),
            'operational_state': forms.Select(attrs={'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'}),
            'year_established': forms.NumberInput(attrs={'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'}),
            'epf_contributors': forms.NumberInput(attrs={'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'}),
            'company_address': forms.Textarea(attrs={'rows': 3, 'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'}),
            'pic_name': forms.TextInput(attrs={'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'}),
            'pic_designation': forms.TextInput(attrs={'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'}),
            'pic_contact_number': forms.TextInput(attrs={'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'}),
            'pic_email': forms.EmailInput(attrs={'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'}),

            # Updated to SELECT widgets for fields with choices
            'contractor_license_class': forms.Select(attrs={'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'}),
            'cidb_grade': forms.Select(attrs={'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'}),
            'cidb_category': forms.Select(attrs={'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'}),

            'sst_number': forms.TextInput(attrs={'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['due_date']  # Exclude due_date from form
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600',
                'placeholder': 'Enter task title'
            }),
            'pic': forms.TextInput(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600',
                'placeholder': 'Person in charge'
            }),
            'document': forms.ClearableFileInput(attrs={
                'class': (
                    'block w-full text-sm text-white bg-gray-700 border border-gray-600 '
                    'rounded-lg cursor-pointer p-3 file:mr-4 file:py-2 file:px-4 '
                    'file:rounded-md file:border-0 file:text-sm file:font-semibold '
                    'file:bg-indigo-600 file:text-white hover:file:bg-indigo-700'
                )
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600 resize-none',
                'rows': 4,
                'placeholder': 'Additional notes or remarks'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'
            }),
        }
