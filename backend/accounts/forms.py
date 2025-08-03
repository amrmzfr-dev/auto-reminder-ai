from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
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
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-lg p-3 border border-gray-600'
            }),
        }
