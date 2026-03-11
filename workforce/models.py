from django.db import models
import uuid
from enum import StrEnum
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.db.models import Q, Sum
from decimal import Decimal
from django.core.validators import MinValueValidator,  MaxValueValidator
from django.conf import settings


class EmploymentType(StrEnum):
    FULL_TIME = "full_time"
    CONTRACT = "contract"


class SalaryType(StrEnum):
    FIXED = "fixed"
    HOURLY = "hourly"

class EmployeeProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="employee_profile",
    )
    company = models.ForeignKey(
        "operations.Company",
        on_delete=models.CASCADE,
        related_name="employees",
    )
    role = models.ForeignKey(
        "accounts.Role",
        on_delete=models.SET_NULL,
        null=True,
        related_name="employees",
    )
    job_title = models.CharField(max_length=100)
    employment_type = models.CharField(
        max_length=20,
        choices=[(e.value, e.value) for e in EmploymentType],
    )
    salary_type = models.CharField(
        max_length=20,
        choices=[(s.value, s.value) for s in SalaryType],
    )
    base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Used when salary_type = fixed",
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Used when salary_type = hourly",
    )
    joining_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def clean(self):
     if self.role and self.company_id:
        if self.role.company_id != self.company_id:
            raise ValidationError("Role must belong to the same company")

    def save(self, *args, **kwargs):  
        self.full_clean()
        previous_role = None
        if self.pk:
            previous_role = (
                EmployeeProfile.objects
                .filter(pk=self.pk)
                .values_list("role_id", flat=True)
                .first()
            )

        super().save(*args, **kwargs)

       
        user = self.user

        
        if previous_role != self.role_id:
            user.groups.clear()

        
        if self.role and self.role.group:
            user.groups.add(self.role.group)   


    @property
    def is_project_manager(self):
        return self.managed_projects.exists()
    

    class Meta:
     constraints = [
        models.CheckConstraint(
            condition=(
                (
                    models.Q(salary_type="fixed") &
                    models.Q(base_salary__isnull=False) &
                    models.Q(hourly_rate__isnull=True)
                ) |
                (
                    models.Q(salary_type="hourly") &
                    models.Q(hourly_rate__isnull=False) &
                    models.Q(base_salary__isnull=True)
                )
            ),
            name="salary_type_strict_validation",
        )
    ]


    def __str__(self):
        return f"{self.user.email} ({self.job_title})"



class TimesheetStatus(models.TextChoices):
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"

class TimesheetPaymentStatus(models.TextChoices):
    UNPAID = "unpaid", "Unpaid"
    PAID = "paid", "Paid"


class Timesheet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    employee = models.ForeignKey(
        "workforce.EmployeeProfile",
        on_delete=models.CASCADE,
        related_name="timesheets"
    )

    project = models.ForeignKey(
        "operations.Project",  
        on_delete=models.CASCADE,
        related_name="timesheets"
    )

    date = models.DateField()

    hours_worked = models.DecimalField(
    max_digits=5,
    decimal_places=2,
    validators=[
        MinValueValidator(Decimal("0.00")), 
        MaxValueValidator(Decimal("24.00"))  
    ]
)

    status = models.CharField(
        max_length=20,
        choices=TimesheetStatus.choices,
        default=TimesheetStatus.SUBMITTED
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_timesheets"
    )

    payed_status = models.CharField(
        max_length=20,
        choices=TimesheetPaymentStatus.choices,
        default=TimesheetPaymentStatus.UNPAID
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

  
    def clean(self):
        
        if self.employee_id and self.project_id:
            if self.employee.company != self.project.company:
                raise ValidationError("Employee and Project must belong to the same company.")

        
        if self.employee_id and self.date:
            total_hours = (
                Timesheet.objects
                .filter(employee_id=self.employee_id, date=self.date)
                .exclude(pk=self.pk)
                .aggregate(total=Sum('hours_worked'))['total'] or 0
            )
            if total_hours + (self.hours_worked or 0) > 24:
                raise ValidationError(
                    f"Cannot log more than 24 hours for {self.employee.user.email} on {self.date}. "
                    f"Already logged: {total_hours} hours."
                )
   
    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.employee} - {self.project} - {self.date}"




class PayrollRunStatus(models.TextChoices):
   
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    


class PayrollRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company = models.ForeignKey(
        "operations.Company",
        on_delete=models.CASCADE,
        related_name="payroll_runs"
    )

    period_start = models.DateField()
    period_end = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=PayrollRunStatus.choices,
        default=PayrollRunStatus.PROCESSING
    )

    processed_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_payroll_runs"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # unique_together = ("company", "period_start", "period_end")
        ordering = ["-period_start"]

    def clean(self):

     if not self.company_id:
        return

     if self.period_start > self.period_end:
        raise ValidationError("Period start must be before period end.")

    #  overlapping = PayrollRun.objects.filter(
    #      company_id=self.company_id,
    #      period_start__lte=self.period_end,
    #      period_end__gte=self.period_start,
    #  )
    #  if self.pk:
    #      overlapping = overlapping.exclude(pk=self.pk)
    #  if overlapping.exists():
    #      raise ValidationError("This payroll period overlaps with an existing payroll run.")

    def save(self, *args, **kwargs):
       
        if self.pk:
            old = PayrollRun.objects.filter(pk=self.pk).first()
            if old and old.status == PayrollRunStatus.COMPLETED:
                raise ValidationError("Completed payroll runs cannot be modified.")

        self.full_clean()
        super().save(*args, **kwargs)



    def __str__(self):
        return f"{self.company} Payroll ({self.period_start} - {self.period_end})"
    



class PayrollItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.CASCADE,
        related_name="items"
    )

    employee = models.ForeignKey(
        "workforce.EmployeeProfile",
        on_delete=models.CASCADE,
        related_name="payroll_items"
    )

    gross_pay = models.DecimalField(max_digits=12, decimal_places=2)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    net_pay = models.DecimalField(
    max_digits=12,
    decimal_places=2,
    editable=False
)

    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("payroll_run", "employee")


    def clean(self):
        if self.deductions > self.gross_pay:
            raise ValidationError("Deductions cannot exceed gross pay.")

  
    def save(self, *args, **kwargs):
        self.full_clean() 
        self.net_pay = self.gross_pay - self.deductions
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - Net: {self.net_pay}"