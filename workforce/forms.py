from django import forms
from .models import Timesheet, EmployeeProfile
from operations.models import EmployeeProject, Project
from django import forms
from .models import EmployeeProfile


class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

       
        if self.current_user and not self.current_user.is_superuser:
            if 'company' in self.fields:
                self.fields.pop('company')  

    def clean(self):
        
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
        user = kwargs.pop("user", None)  
        super().__init__(*args, **kwargs)

        if user:
            employee = getattr(user, "employee_profile", None)
            if employee:
                
                assigned_project_ids = EmployeeProject.objects.filter(
                    employee=employee
                ).values_list("project_id", flat=True)
                self.fields["project"].queryset = Project.objects.filter(
                    id__in=assigned_project_ids
                )
            else:
                self.fields["project"].queryset = Project.objects.none()
        else:
            self.fields["project"].queryset = Project.objects.none()


    def clean(self):
        cleaned_data = super().clean()
        try:
          
            self.instance.clean()
        except forms.ValidationError as e:
            
            raise forms.ValidationError(
                e.message_dict.get('__all__', e.messages)
            )
        return cleaned_data        
