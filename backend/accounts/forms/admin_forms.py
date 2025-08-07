# admin_forms.py

# Import necessary modules from Django.
# 'forms' provides the form-building classes.
# 'UserCreationForm' is a special ModelForm for creating new users, handling password validation and hashing.
from django import forms
from django.contrib.auth.forms import UserCreationForm

# Import the models this form will be interacting with.
# The '.' indicates a relative import from the models.py file within the same app.
from ..models import Task, CustomUser

# -----------------------------------------------------------------------------
# Admin Registration Form
# -----------------------------------------------------------------------------
# This form handles the creation of new users by an admin.
# It inherits from UserCreationForm to leverage its built-in user creation logic.
class AdminRegistrationForm(UserCreationForm):
    class Meta:
        """
        The Meta class provides configuration for the form.
        It links the form to a model and specifies which fields to include.
        """
        # This form is built for the CustomUser model.
        model = CustomUser
        
        # Only the 'username' field will be displayed on the form.
        # The password fields are automatically included by UserCreationForm.
        fields = ('username',)

    def save(self, commit=True):
        """
        Overrides the default save method to add custom logic.
        This is where we assign a specific role to the user being created.
        """
        # Call the parent class's save method but with commit=False.
        # This creates a user object in memory without saving it to the database yet,
        # allowing us to modify it first.
        user = super().save(commit=False)
        
        # Force the 'role' attribute of the new user to '1' (representing the 'admin' role).
        # This ensures any user created with this form is automatically an admin.
        user.role = '1'
        
        # If commit is True (which it is by default), save the user object to the database.
        if commit:
            user.save()
            
        # Return the newly created and saved user instance.
        return user

# -----------------------------------------------------------------------------
# Task Creation/Update Form
# -----------------------------------------------------------------------------
# This is a ModelForm for creating and editing 'Task' objects.
# ModelForms are convenient as they automatically generate form fields from a model.
class TaskForm(forms.ModelForm):
    class Meta:
        """
        Configures the TaskForm, linking it to the Task model and customizing its fields.
        """
        # Specifies that this form is for the 'Task' model.
        model = Task
        
        # 'exclude' is used to specify fields from the model that should NOT be included in the form.
        # Here, we are preventing 'due_date' from being set via this form.
        exclude = ['due_date']
        
        # The 'widgets' dictionary allows for customizing the HTML input element for each form field.
        # 'attrs' is used to set HTML attributes like 'class', 'placeholder', etc., for styling and UX.
        # The CSS classes used (e.g., 'w-full', 'bg-gray-700') suggest a Tailwind CSS framework is being used.
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
                # This widget provides a checkbox to clear the file field if it already has a file.
                'class': (
                    'block w-full text-sm text-white bg-gray-700 border border-gray-600 '
                    'rounded-md cursor-pointer p-3 file:mr-4 file:py-2 file:px-4 '
                    'file:rounded-md file:border-0 file:text-sm file:font-semibold '
                    'file:bg-indigo-600 file:text-white hover:file:bg-indigo-700'
                )
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600 resize-none',
                'rows': 4,  # Sets the visible height of the textarea to 4 rows.
                'placeholder': 'Additional notes or remarks'
            }),
            'priority': forms.Select(attrs={
                # This widget renders as an HTML <select> dropdown.
                'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600'
            }),
            'status': forms.Select(attrs={
                # This widget also renders as an HTML <select> dropdown.
                'class': 'w-full bg-gray-700 text-white rounded-md p-3 border border-gray-600'
            }),
        }