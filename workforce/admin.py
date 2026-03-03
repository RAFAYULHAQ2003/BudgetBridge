from decimal import Decimal
from django import forms
from django.contrib import admin
from django.conf import settings
from .models import EmployeeProfile, Timesheet, PayrollRun, PayrollItem, TimesheetStatus, PayrollRunStatus
from operations.models import Project
from accounts.models import Role
from workforce.services import generate_payroll 
import csv
from django.http import HttpResponse
from .forms import EmployeeProfileForm


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    form = EmployeeProfileForm
    list_display = ("user", "company", "role", "job_title", "employment_type", "salary_type")
    list_filter = ("company", "role", "employment_type", "salary_type")
    search_fields = ("user__email", "job_title")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)
    
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        # Remove 'company' from form for non-superusers
        if not request.user.is_superuser and 'company' in fields:
            fields = [f for f in fields if f != 'company']
        return fields
    
    def get_form(self, request, obj=None, **kwargs):
        # Pass current_user to the form
        kwargs['form'] = self.form
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def save_model(self, request, obj, form, change):
        # Force company assignment for non-superusers
        if not request.user.is_superuser:
            obj.company = request.user.company
        super().save_model(request, obj, form, change)


    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if not request.user.is_superuser:
    #         if db_field.name == "user":
    #             kwargs["queryset"] = db_field.related_model.objects.filter(company=request.user.company)
    #         if db_field.name == "role":
    #             kwargs["queryset"] = Role.objects.filter(company=request.user.company)
    #     # Call the parent's formfield_for_foreignkey to handle the `company` field if needed
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
     if db_field.name == "user" and not request.user.is_superuser:
        from accounts.models import User
        # Correct related name
        kwargs["queryset"] = User.objects.filter(
            company=request.user.company
        ).exclude(
            employee_profile__isnull=False  # <-- use the correct related_name from User->EmployeeProfile
        )
     if db_field.name == "role" and not request.user.is_superuser:
        kwargs["queryset"] = Role.objects.filter(company=request.user.company)
     return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ("employee", "project", "date", "hours_worked", "status")
    list_filter = ("status", "project")
    search_fields = ("employee__user__email", "project__name")
    actions = ["approve_timesheets"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(employee__company=request.user.company)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "employee":
                kwargs["queryset"] = EmployeeProfile.objects.filter(company=request.user.company)
            if db_field.name == "project":
                kwargs["queryset"] = Project.objects.filter(company=request.user.company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.action(description="Mark selected timesheets as Approved")
    def approve_timesheets(self, request, queryset):
        updated_count = queryset.update(status=TimesheetStatus.APPROVED)
        self.message_user(request, f"{updated_count} timesheets marked as Approved.")



class PayrollItemInline(admin.TabularInline):
    model = PayrollItem
    readonly_fields = ("employee", "gross_pay", "deductions", "net_pay")
    extra = 0




@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
#class PayrollRunAdmin(BaseCompanyAdmin):
    list_display = ("company", "period_start", "period_end", "status", "processed_at")
    list_filter = ("company", "status")
    date_hierarchy = "period_start"
    search_fields = ("company__name",)
    inlines = [PayrollItemInline]
    actions = ["generate_payroll_items"]
    actions = ["generate_payroll_action"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)

    def save_model(self, request, obj, form, change):
       
        super().save_model(request, obj, form, change)

        #
        if obj.status == "completed":
         if obj.status == "completed" and not change: 
            # Avoid generating again if items already exist
            if not obj.items.exists():
                generate_payroll(obj)
                self.message_user(request, "Payroll items generated automatically.")

    @admin.action(description="Generate PayrollItems for selected Payroll Runs")
    def generate_payroll_items(self, request, queryset):
     def generate_payroll_action(self, request, queryset):
        for payroll_run in queryset:
            
            if payroll_run.status == "completed":
           
             if not payroll_run.items.exists():
                generate_payroll(payroll_run)
                self.message_user(request, "Payroll items generated successfully.")
                self.message_user(request, f"Payroll items generated for {payroll_run}.")
             else:
                self.message_user(request, f"Payroll items already exist for {payroll_run}.", level='WARNING')





@admin.action(description="Export selected PayrollItems as CSV")
def export_as_csv(modeladmin, request, queryset):
   
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payroll_items.csv"'

    writer = csv.writer(response)

    writer.writerow(['Employee', 'Email', 'Payroll Run', 'Gross Pay', 'Deductions', 'Net Pay', 'Generated At'])

    # Write data rows
    for item in queryset:
        writer.writerow([
            item.employee.user.get_full_name(),
            item.employee.user.email,
            f"{item.payroll_run.period_start} to {item.payroll_run.period_end}",
            item.gross_pay,
            item.deductions,
            item.net_pay,
            item.generated_at
        ])

    return response



@admin.register(PayrollItem)
class PayrollItemAdmin(admin.ModelAdmin):
    list_display = ("employee", "payroll_run", "gross_pay", "deductions", "net_pay")
    list_filter = ("payroll_run",)
    search_fields = ("employee__user__email", "payroll_run__company__name")
    actions = [export_as_csv]  # <-- add this line
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(payroll_run__company=request.user.company)



