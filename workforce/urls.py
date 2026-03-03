from django.urls import path
from .views import (
    MyTimesheetListView,
    TimesheetCreateView,
    TimesheetUpdateView,
    TimesheetDeleteView,
    ProjectTimesheetListView,
    TimesheetApproveView,
    PayrollRunListView,
    PayrollRunCreateView,
    MyPayrollView,
)

urlpatterns = [
    path("", MyTimesheetListView.as_view(), name="my_timesheets"),
    path("add/", TimesheetCreateView.as_view(), name="timesheet_add"),
    path("<uuid:pk>/edit/", TimesheetUpdateView.as_view(), name="timesheet_edit"),
    path("<uuid:pk>/delete/", TimesheetDeleteView.as_view(), name="timesheet_delete"),
    path("project-timesheets/", ProjectTimesheetListView.as_view(), name="project_timesheets"),
    path("approve/<uuid:pk>/", TimesheetApproveView.as_view(), name="approve_timesheet"),
    path("", PayrollRunListView.as_view(), name="payroll_list"),
    path("create/", PayrollRunCreateView.as_view(), name="payroll_run_create"),
    path("my/", MyPayrollView.as_view(), name="my_payroll"),

]
