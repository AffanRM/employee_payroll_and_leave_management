from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required # type: ignore
from django.contrib.auth import logout
# Import our models and forms
from .models import Employee, LeaveRequest, Notification
from .forms import EmployeeRegistrationForm, LeaveRequestForm, EmployeeUpdateForm

def register(request):
    if request.method == "POST":
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            # Django's built-in authentication requires is_active=True to allow login
            employee.is_active = True  
            # We use our own defined field to indicate whether an employee has been approved or not
            employee.is_approved = False  
            # Save the employee to the database and redirect to the login page
            employee.save()
            return redirect('login')
    else:
        # If the form was not submitted then generate the form and display it
        form = EmployeeRegistrationForm()
    return render(request, 'employees/register.html', {'form': form})


# Define the function for what happens if the user tries to login 
def login_view(request):
    error_message = None
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # User exists and password was entered correctly
            if user.is_approved:  # Check if user is approved
                login(request, user)
                # Redirect based on user role (i.e manager or employee)
                if user.is_staff:
                    manager_log = True
                else:
                    manager_log = False
                if manager_log:
                    return redirect('manager_dashboard')
                else:
                    return redirect('dashboard')
            else:
                error_message = "Your account is pending approval. Please wait for admin confirmation."
        else:
            error_message = "Invalid username or password. Please try again."
            
    return render(request, 'employees/login.html', {'error_message': error_message})


# Only display the dashboard if the employee is logged in
@login_required
def dashboard(request):
    annual_leaves = request.user.annual_leave_balance
    sick_leaves = request.user.sick_leave_balance
    leave_balances = {
        'Annual': annual_leaves,
        'Sick': sick_leaves
    }
    # Check the unread notfications and render them
    unread_notifications = Notification.objects.filter(employee=request.user, is_read=False).count()

    return render(request, 'employees/dashboard.html', {
        'user': request.user,
        'leave_balances': leave_balances,
        'unread_notifications': unread_notifications
    })


# The employee can only apply for a leave if they are logged in
@login_required
def apply_leave(request):
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user
            leave.save()
            # After the employee applies for a leave, redirect them back to the dashboard
            return redirect('dashboard')
    else:
        form = LeaveRequestForm()
    return render(request, 'employees/apply_leave.html', {'form': form, 'user': request.user})


# Only the manager can approve the leave request
@staff_member_required
def approve_leave(request, leave_id):

    # The 404 page will be returned if trying to approve a leave that does not exist
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    leave.status = "Approved"
    # Calculate leave duration
    leave_days = (leave.end_date - leave.start_date).days
    # Add one as (e.g if leave for one day 20th March then 20-20 is 0 but that is 1 leave)
    leave_days += 1
    
    # Update leave balance based on leave type
    if leave.leave_type == 'Annual':
        leave.employee.annual_leave_balance -= leave_days
    elif leave.leave_type == 'Sick':
        leave.employee.sick_leave_balance -= leave_days
    
    # Save to the database
    leave.employee.save()
    leave.save()

    # Create notification for employee
    Notification.objects.create(
        employee=leave.employee,
        message=f"Your {leave.get_leave_type_display()} request from {leave.start_date} to {leave.end_date} has been approved."
    )

    return redirect('admin_dashboard')


# The manager can update employee details
@staff_member_required
def update_employee(request, employee_id):
    employee = Employee.objects.get(id=employee_id)
    if request.method == "POST":
        form = EmployeeUpdateForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            # After updating the employee information, return to the employee list page
            return redirect('employee_list')
    else:
        form = EmployeeUpdateForm(instance=employee)
    return render(request, 'employees/update_employee.html', {'form': form, 'employee': employee})


@staff_member_required
def employee_list(request):
    # Get all the employees and display them
    employees = Employee.objects.all()
    return render(request, 'employees/employee_list.html', {'employees': employees})


@login_required
def profile(request):
    leave_requests = LeaveRequest.objects.filter(employee=request.user)
    return render(request, 'employees/profile.html', {
        'employee': request.user,
        'leave_requests': leave_requests
    })


@staff_member_required
def deactivate_employee(request, employee_id):
    employee = Employee.objects.get(id=employee_id)
    if request.method == "POST":
        #employee.is_active = False
        employee.is_approved = False
        employee.save()
        return redirect('employee_list')
    return render(request, 'employees/deactivate_employee.html', {'employee': employee})


@login_required
def view_leave_requests(request):
    leave_requests = LeaveRequest.objects.filter(employee=request.user)
    return render(request, 'employees/view_leave_requests.html', {'leave_requests': leave_requests})


@staff_member_required
def manager_dashboard(request):
    pending_leave_requests = LeaveRequest.objects.filter(status='Pending')
    return render(request, 'employees/manager_dashboard.html', {'pending_requests': pending_leave_requests})


@staff_member_required
def review_leave(request, leave_id):

    leave = LeaveRequest.objects.get(id=leave_id)
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'approve':
            # Logic to deduct from leave balance
            duration = leave.get_duration()
            if leave.leave_type == 'Annual':
                leave.employee.annual_leave_balance -= duration
            elif leave.leave_type == 'Sick':
                leave.employee.sick_leave_balance -= duration
            leave.employee.save()
            
            leave.status = 'Approved'
            leave.save()
            
            # Create notification
            Notification.objects.create(
                employee=leave.employee,
                message=f"Your {leave.get_leave_type_display()} request from {leave.start_date} to {leave.end_date} has been approved."
            )
        elif action == 'reject':
            leave.status = 'Rejected'
            leave.save()
            
            # Create notification
            Notification.objects.create(
                employee=leave.employee,
                message=f"Your {leave.get_leave_type_display()} request from {leave.start_date} to {leave.end_date} has been rejected."
            )

        return redirect('manager_dashboard')
    
    return render(request, 'employees/review_leave.html', {'leave': leave})


@login_required
def notifications(request):
    notifications = Notification.objects.filter(employee=request.user).order_by('-created_at')
    
    # Mark notifications as read
    unread = notifications.filter(is_read=False)
    unread.update(is_read=True)
    
    return render(request, 'employees/notifications.html', {'notifications': notifications})


@staff_member_required
def approve_employee(request, employee_id):
    
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == "POST":
        employee.is_approved = True
        employee.save()
        
        # Create notification for the employee
        Notification.objects.create(
            employee=employee,
            message="Your account has been approved. You can now log in to the system."
        )
        
        return redirect('employee_list')
    return render(request, 'employees/approve_employee.html', {'employee': employee})


# Define a view to logout the users (managers and employees)
def logout_view(request):
    logout(request)
    return redirect('login')