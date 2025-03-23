from django.contrib import admin
from .models import Employee, LeaveRequest

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'department', 'is_approved')
    actions = ['approve_employees']

    def approve_employees(self, request, queryset):
        queryset.update(is_approved=True)

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(LeaveRequest)
