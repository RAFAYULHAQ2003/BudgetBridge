from django import forms
from .models import Timesheet, EmployeeProfile
from operations.models import Project
from django import forms
from .models import EmployeeProfile


class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

        # Hide company field completely for non-superusers
        if self.current_user and not self.current_user.is_superuser:
            if 'company' in self.fields:
                self.fields.pop('company')  # remove from form entirely

    def clean(self):
        # Assign company automatically for non-superusers
        if self.current_user and not self.current_user.is_superuser:
            self.instance.company = self.current_user.company
        return super().clean()

class TimesheetForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ["project", "date", "hours_worked"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "hours_worked": forms.NumberInput(attrs={"step": 0.1}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # get user from view
        super().__init__(*args, **kwargs)

        if user:
            employee = getattr(user, "employee_profile", None)
            if employee:
                # Filter projects by employee's company
                self.fields["project"].queryset = Project.objects.filter(
                    company=employee.company
                )
            else:
                # If user has no employee profile, show no projects
                self.fields["project"].queryset = Project.objects.none()
        else:
            self.fields["project"].queryset = Project.objects.none()
