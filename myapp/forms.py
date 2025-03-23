from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Employee
from .models import LeaveRequest  # ✅ Add this import

class EmployeeRegistrationForm(UserCreationForm):
    department = forms.CharField(max_length=100)

    class Meta:
        model = Employee
        fields = ['username', 'email', 'password1', 'password2', 'department']


# forms.py - Update the LeaveRequestForm
class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'})
        }


# For updating the employee details
class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'department', 'is_approved']