from django import forms
from .models import Expense, PaymentMethod, ProjectPaymentInvoice
from operations.models import Project
from django.utils import timezone
from .models import Invoice, Payment, PaymentStatus
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





class ClientBillingInvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "project",
            "invoice_no",
            "issue_date",
            "due_date",
            "subtotal",
            "tax_percentage",
            "discount_amount",
            "notes",
        ]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.company:
            self.fields["project"].queryset = Project.objects.filter(
                company=user.company,
                client__isnull=False
            ).select_related("client")

        self.fields["issue_date"].initial = timezone.now().date()
        self.fields["due_date"].initial = timezone.now().date()

    def clean_project(self):
        project = self.cleaned_data.get("project")
        if not project.client:
            raise forms.ValidationError("Selected project must have a client.")
        return project


class ProjectPaymentInvoiceForm(forms.ModelForm):
    class Meta:
        model = ProjectPaymentInvoice
        fields = ["project", "amount","description",  "tax_percentage", "discount_amount", "due_date"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = Project.objects.filter(company=user.company)

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        project = self.cleaned_data.get("project")
        if project:
            total_invoiced = sum(inv.amount for inv in project.payment_invoices.all())
            remaining_budget = project.budget - total_invoiced
            if amount > remaining_budget:
                raise forms.ValidationError(
                    f"Amount cannot exceed remaining project budget ({remaining_budget})."
                )
        return amount


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount", "payment_method", "status", "transaction_ref", "paid_at"]
        widgets = {
            "status": forms.Select(choices=PaymentStatus.choices),
            "payment_method": forms.Select(choices=PaymentMethod.choices),
            "paid_at": forms.DateTimeInput(attrs={"type": "datetime-local"})
        }

    def __init__(self, *args, **kwargs):
        self.invoice = kwargs.pop("invoice")
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        confirmed_total = sum(
            p.amount for p in self.invoice.payments.filter(status="confirmed")
        )
        if self.cleaned_data.get("status") == "confirmed":
            if confirmed_total + amount > self.invoice.total_amount:
                raise forms.ValidationError("Payment exceeds invoice total.")
        return amount

