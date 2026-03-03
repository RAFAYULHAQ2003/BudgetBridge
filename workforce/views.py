from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from workforce.models import Timesheet, EmployeeProfile
from .forms import TimesheetForm
from operations.models import Project
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib import messages

from workforce.services import generate_payroll
from workforce.models import PayrollRun, PayrollItem


class MyTimesheetListView(LoginRequiredMixin, ListView):
    model = Timesheet
    template_name = "workforce/timesheet/my_list.html"
    context_object_name = "timesheets"

    def get_queryset(self):
        try:
            employee = EmployeeProfile.objects.get(user=self.request.user)
            return Timesheet.objects.filter(employee=employee).order_by("-date")
        except EmployeeProfile.DoesNotExist:
            return Timesheet.objects.none()


class TimesheetCreateView(LoginRequiredMixin, CreateView):
    model = Timesheet
    form_class = TimesheetForm
    template_name = "workforce/timesheet/form.html"
    success_url = reverse_lazy("my_timesheets")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            employee = EmployeeProfile.objects.get(user=self.request.user)
        except EmployeeProfile.DoesNotExist:
            raise ValidationError("No employee profile linked to your account.")

        form.instance.employee = employee
        form.instance.status = "submitted"  # New timesheets are submitted directly
        return super().form_valid(form)


class TimesheetUpdateView(LoginRequiredMixin, UpdateView):
    model = Timesheet
    form_class = TimesheetForm
    template_name = "workforce/timesheet/form.html"
    success_url = reverse_lazy("my_timesheets")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        # Only allow editing own timesheets that are submitted
        if obj.employee.user != request.user:
            raise PermissionDenied("Cannot edit another user's timesheet.")
        if obj.status != "submitted":
            raise PermissionDenied("Only submitted timesheets can be edited.")

        return super().dispatch(request, *args, **kwargs)


class TimesheetDeleteView(LoginRequiredMixin, DeleteView):
    model = Timesheet
    template_name = "workforce/timesheet/confirm_delete.html"
    success_url = reverse_lazy("my_timesheets")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        # Only allow deleting own timesheets that are submitted
        if obj.employee.user != request.user:
            raise PermissionDenied("Cannot delete another user's timesheet.")
        if obj.status != "submitted":
            raise PermissionDenied("Only submitted timesheets can be deleted.")

        return super().dispatch(request, *args, **kwargs)
    

class ProjectTimesheetListView(LoginRequiredMixin, ListView):
    model = Timesheet
    template_name = "workforce/timesheet/project_list.html"
    context_object_name = "timesheets"

    def get_queryset(self):
        # get project manager object linked to user
        try:
            manager = EmployeeProfile.objects.get(user=self.request.user)
        except EmployeeProfile.DoesNotExist:
            return Timesheet.objects.none()

        managed_projects = Project.objects.filter(project_manager__user=self.request.user)
        return Timesheet.objects.filter(project__in=managed_projects).order_by("-date")
    
class TimesheetApproveView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        timesheet = get_object_or_404(Timesheet, pk=pk)

        # Only the project manager of this timesheet's project can approve
        if timesheet.project.project_manager.user != request.user:
            raise PermissionDenied("You are not the manager of this project.")

        # Only submitted timesheets can be approved
        if timesheet.status != "submitted":
            raise PermissionDenied("Only submitted timesheets can be approved.")

        timesheet.status = "approved"
        timesheet.save()
        return redirect("project_timesheets")
    


class MyPayrollView(LoginRequiredMixin, ListView):
    model = PayrollItem
    template_name = "payroll/my_payroll.html"
    context_object_name = "payroll_items"

    def get_queryset(self):
        return PayrollItem.objects.filter(employee=self.request.user.employee_profile).order_by('-payroll_run__period_start')

from django.forms import ValidationError as FormValidationError

class PayrollRunCreateView(LoginRequiredMixin, CreateView):
    model = PayrollRun
    fields = ["period_start", "period_end"]
    template_name = "payroll/payroll_run_form.html"

    def form_valid(self, form):
        form.instance.company = self.request.user.company
        form.instance.created_by = self.request.user
        try:
            response = super().form_valid(form)
            generate_payroll(form.instance)
            messages.success(self.request, "Payroll generated successfully!")
            return response
        except ValidationError as e:
            # Attach the error to the form so it shows in the template
            form.add_error(None, e)  # None attaches it to the non-field errors
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Payroll generation failed: {e}")
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("payroll_list")
    
class PayrollRunListView(LoginRequiredMixin, ListView):
    model = PayrollRun
    template_name = "payroll/payroll_list.html"
    context_object_name = "payroll_runs"

    def get_queryset(self):
        return PayrollRun.objects.filter(company=self.request.user.company)    

