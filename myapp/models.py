from django.contrib.auth.models import AbstractUser
from django.db import models

class Employee(AbstractUser):
    is_approved = models.BooleanField(default=False)  # Admin approval required
    department = models.CharField(max_length=100, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # models.py - Add these fields to the Employee model
    annual_leave_balance = models.DecimalField(max_digits=5, decimal_places=1, default=21.0)
    sick_leave_balance = models.DecimalField(max_digits=5, decimal_places=1, default=10.0)
    
    def __str__(self):
        return self.username

# models.py - Update the LeaveRequest model
class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('Annual', 'Annual Leave'),
        ('Sick', 'Sick Leave'),
        ('Other', 'Other')
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, default='Annual')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} - {self.status}"
        
    def get_duration(self):
        return (self.end_date - self.start_date).days + 1
    

# The model for managing notifications
class Notification(models.Model):
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.employee.username} - {self.message[:30]}"
