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
                attrs={"type": "date", "class": "form-control"}
            ),
            "amount": forms.NumberInput(
                attrs={"class": "form-control mono", "step": "0.01", "min": "0", "placeholder": "0.00"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Briefly describe the expense…"}
            ),
            "project": forms.Select(
                attrs={"class": "form-control"}
            ),
            "category": forms.Select(
                attrs={"class": "form-control"}
            ),
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

       
        for field in self.fields.values():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-control"




class CompanyExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["category", "amount", "description", "expense_date"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user and hasattr(self.user, "company"):
            self.fields["category"].queryset = self.fields["category"].queryset.filter(
                company=self.user.company
            )    
