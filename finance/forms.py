# finance/forms.py
from django import forms
from .models import Expense
from operations.models import Project

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["project", "category", "amount", "description", "expense_date"]
        widgets = {
            "expense_date": forms.DateInput(
                attrs={"type": "date"}  # this will render an HTML5 date picker
            )
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user") 
        super().__init__(*args, **kwargs)
       
        self.fields["project"].queryset = Project.objects.filter(
            employee_assignments__employee=user.employee_profile
        )
        self.fields["category"].queryset = self.fields["category"].queryset.filter(
            is_active=True
        )