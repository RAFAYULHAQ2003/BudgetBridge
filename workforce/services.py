from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.db.models import Sum
from workforce.models import (
    PayrollRun,
    PayrollItem,
    Timesheet,
    EmployeeProfile,
    TimesheetStatus,
    SalaryType,
)
import datetime


def generate_payroll(payroll_run: PayrollRun):
   
    employees = EmployeeProfile.objects.filter(
        company=payroll_run.company,
        is_active=True
    )

    num_working_days = sum(
        1
        for i in range(
            (payroll_run.period_end - payroll_run.period_start).days + 1)
        if (
            payroll_run.period_start + datetime.timedelta(days=i)
        ).weekday() < 5
    )

    expected_hours = Decimal(num_working_days * 8)

    with transaction.atomic():
        for employee in employees:

           
            total_hours = (
                Timesheet.objects.filter(
                    employee=employee,
                    status=TimesheetStatus.APPROVED,
                    date__gte=payroll_run.period_start,
                    date__lte=payroll_run.period_end,
                ).aggregate(total=Sum("hours_worked"))["total"]
                or Decimal("0.00")
            )

            total_hours = total_hours.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

      
            if employee.salary_type == SalaryType.HOURLY:

                hourly_rate = employee.hourly_rate or Decimal("0.00")
                gross_pay = total_hours * hourly_rate

          
            else:

                base_salary = employee.base_salary or Decimal("0.00")

               
                month_start = payroll_run.period_start.replace(day=1)

                if payroll_run.period_start.month == 12:
                    next_month = payroll_run.period_start.replace(
                        year=payroll_run.period_start.year + 1,
                        month=1,
                        day=1,
                    )
                else:
                    next_month = payroll_run.period_start.replace(
                        month=payroll_run.period_start.month + 1,
                        day=1,
                    )

                month_end = next_month - datetime.timedelta(days=1)

                total_month_working_days = sum(
                    1
                    for i in range(
                        (month_end - month_start).days + 1
                    )
                    if (
                        month_start + datetime.timedelta(days=i)
                    ).weekday() < 5
                )

               
                per_day_salary = (
                    base_salary / Decimal(total_month_working_days)
                    if total_month_working_days > 0
                    else Decimal("0.00")
                )

              
                period_salary_cap = per_day_salary * Decimal(num_working_days)

                if expected_hours == 0:
                    gross_pay = Decimal("0.00")

                elif total_hours >= expected_hours:
                    
                    gross_pay = period_salary_cap

                else:
                    
                    work_ratio = total_hours / expected_hours
                    gross_pay = period_salary_cap * work_ratio

           
            gross_pay = gross_pay.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            
            PayrollItem.objects.update_or_create(
                payroll_run=payroll_run,
                employee=employee,
                defaults={
                    "gross_pay": gross_pay,
                    "deductions": Decimal("0.00"),
                    "net_pay": gross_pay,
                },
            )
