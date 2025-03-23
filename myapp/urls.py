from django.urls import path
#from .views import home
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('apply-leave/', apply_leave, name='apply_leave'),
    path('employees/', employee_list, name='employee_list'),
    path('employees/update/<int:employee_id>/', update_employee, name='update_employee'),
    path('profile/', profile, name='profile'),
    path('employees/deactivate/<int:employee_id>/', deactivate_employee, name='deactivate_employee'),
    path('leave-requests/', view_leave_requests, name='view_leave_requests'),
    path('manager/', manager_dashboard, name='manager_dashboard'),
    path('review-leave/<int:leave_id>/', review_leave, name='review_leave'),
    path('notifications/', notifications, name='notifications'),
    path('logout/', logout_view, name='logout'),
]
