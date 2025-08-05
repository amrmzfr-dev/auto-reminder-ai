from django import forms
from .models import Task
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, InstallerProfile

class InstallerRegistrationForm(UserCreationForm):
    # InstallerProfile fields
    company_name = forms.CharField(max_length=255)
    company_ssm_number = forms.CharField(max_length=50)
    operational_state = forms.ChoiceField(choices=InstallerProfile._meta.get_field('operational_state').choices)
    pic_name = forms.CharField(max_length=255)
    pic_designation = forms.CharField(max_length=100)
    pic_contact_number = forms.CharField(max_length=15)

    # Optional fields
    company_address = forms.CharField(widget=forms.Textarea, required=False)
    year_established = forms.IntegerField(required=False)
    epf_contributors = forms.IntegerField(required=False)

    is_st_registered = forms.BooleanField(required=False)
    contractor_license_class = forms.ChoiceField(choices=[('', '---'), ('A', 'A'), ('B', 'B'), ('C', 'C')], required=False)
    is_cidb_registered = forms.BooleanField(required=False)
    cidb_category = forms.CharField(required=False)
    cidb_grade = forms.CharField(required=False)
    is_sst_registered = forms.BooleanField(required=False)
    sst_number = forms.CharField(required=False)
    has_insurance = forms.BooleanField(required=False)
    has_coi_history = forms.BooleanField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']

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
