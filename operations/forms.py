from django import forms

from workforce.models import EmployeeProfile
from .models import Project, Client, EmployeeProject

class ProjectWithClientForm(forms.ModelForm):
    # Nested client fields
    client_name = forms.CharField(
        max_length=255, 
        required=True, 
        label="Client Name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    client_email = forms.EmailField(
        required=True, 
        label="Client Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    client_phone = forms.CharField(
        max_length=30, 
        required=False, 
        label="Client Phone",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    client_address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False, 
        label="Client Address"
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'project_manager', 'budget', 'start_date', 'end_date', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'project_manager': forms.Select(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control mono', 'step': '0.01', 'min': '0'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # pass logged-in user
        super().__init__(*args, **kwargs)

        # Limit project manager choices to employees of the user's company
        if self.user and getattr(self.user, 'employee_profile', None):
            company = self.user.employee_profile.company
            self.fields['project_manager'].queryset = EmployeeProfile.objects.filter(company=company)
        else:
            self.fields['project_manager'].queryset = EmployeeProfile.objects.none()

class EmployeeProjectForm(forms.ModelForm):
    class Meta:
        model = EmployeeProject
        fields = ['employee', 'role_in_project']

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)  # pass company
        super().__init__(*args, **kwargs)
        if company:
            self.fields['employee'].queryset = EmployeeProfile.objects.filter(company=company)
        else:
            self.fields['employee'].queryset = EmployeeProfile.objects.none()
