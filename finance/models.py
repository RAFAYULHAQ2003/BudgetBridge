# from datetime import timezone
import uuid
from decimal import ROUND_HALF_UP, Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from operations.models import Company, Project, Client


class ExpenseCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company = models.ForeignKey(
        "operations.Company",
        on_delete=models.CASCADE,
        related_name="expense_categories"
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("company", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.company.name})"




class ExpenseStatus(models.TextChoices):
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
   


class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company = models.ForeignKey(
        "operations.Company",
        on_delete=models.CASCADE,
        related_name="expenses"
    )

    project = models.ForeignKey(
        "operations.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses"
    )

    employee = models.ForeignKey(
        "workforce.EmployeeProfile",
        on_delete=models.CASCADE,
        related_name="expenses"
    )

    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name="expenses"
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)

    description = models.TextField(blank=True)
    #receipt = models.FileField(upload_to="expenses/", blank=True, null=True)

    expense_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=ExpenseStatus.choices,
        default=ExpenseStatus.SUBMITTED
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_expenses"
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
    

     if self.project_id and self.company_id:
        if self.project.company_id != self.company_id:
            raise ValidationError("Project must belong to same company.")

     if self.employee_id and self.company_id:
        if self.employee.company_id != self.company_id:
            raise ValidationError("Employee must belong to same company.")

     if self.category_id and self.company_id:
        if self.category.company_id != self.company_id:
            raise ValidationError("Category must belong to same company.")

    class Meta:
        ordering = ["-expense_date"]
        indexes = [
            models.Index(fields=["company", "status"]),
        ]

    def __str__(self):
        return f"{self.employee} - {self.amount}"



class InvoiceStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SENT = "sent", "Sent"
    PARTIAL = "partial", "Partial"
    PAID = "paid", "Paid"
    OVERDUE = "overdue", "Overdue"


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company = models.ForeignKey(
        "operations.Company",
        on_delete=models.CASCADE,
        related_name="invoices"
    )

    expense = models.OneToOneField(
    "finance.Expense",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="invoice"
)

    client = models.ForeignKey(
        "operations.Client",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="invoices"
    )

    project = models.ForeignKey(
        "operations.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices"
    )
    
    invoice_no = models.CharField(max_length=50)
    invoice_sent = models.BooleanField(default=False)
    issue_date = models.DateField()
    due_date = models.DateField()

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT
    )

    notes = models.TextField(blank=True)
    

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_invoices"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("company", "invoice_no")
        ordering = ["-issue_date"]


    def clean(self):
        if self.client and self.company:
            if self.client.company_id != self.company_id:
                raise ValidationError("Client must belong to same company.")

        if self.project and self.company:
            if self.project.company_id != self.company_id:
                raise ValidationError("Project must belong to same company.")

        if self.issue_date and self.due_date:
            if self.issue_date > self.due_date:
                raise ValidationError("Issue date cannot be after due date.")

    def calculate_totals(self):
        self.tax_amount = (self.subtotal * self.tax_percentage) / Decimal("100")
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount

    def save(self, *args, **kwargs):
        self.calculate_totals()
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def amount_paid(self):
        return self.payments.filter(
            status="confirmed"
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    @property
    def balance_due(self):
        return max(self.total_amount - self.amount_paid, Decimal("0.00"))

    def update_payment_status(self):
        paid = self.amount_paid

        if paid <= Decimal("0.00"):
            self.status = InvoiceStatus.SENT if self.invoice_sent else InvoiceStatus.DRAFT
        elif paid < self.total_amount:
            self.status = InvoiceStatus.PARTIAL
        else:
            self.status = InvoiceStatus.PAID

        if self.status != InvoiceStatus.PAID and self.due_date < timezone.now().date():
            self.status = InvoiceStatus.OVERDUE

        self.save(update_fields=["status"])
   

class InvoiceItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items"
    )

    description = models.TextField()
    category = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False
    )

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description




def generate_invoice_no():
     return f"INV-{timezone.now().timestamp()}"

def default_issue_date():
    return timezone.now().date()


class ProjectPaymentInvoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="payment_invoices")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="payment_invoices")
    invoice_no = models.CharField(max_length=50, unique=True, default=generate_invoice_no)
    issue_date = models.DateField(default=default_issue_date)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(max_length=50,default="Project Payment Invoice")
    status = models.CharField(max_length=20, choices=InvoiceStatus.choices, default="sent")

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    invoice_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issue_date"]

    def clean(self):
        # if self.project.company_id != self.company_id:
        #     raise ValidationError("Project must belong to the same company.")
        if self.issue_date > self.due_date:
            raise ValidationError("Issue date cannot be after due date.")

    def calculate_totals(self):
        # self.tax_amount = (self.amount * self.tax_percentage) / Decimal("100")
        # self.total_amount = self.amount + self.tax_amount - self.discount_amount
        self.tax_amount = (self.amount * self.tax_percentage / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.total_amount = (self.amount + self.tax_amount - self.discount_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def save(self, *args, **kwargs):
        self.calculate_totals()
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def amount_paid(self):
        total_paid = self.payments.filter(status="confirmed").aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0.00")
        return total_paid

    @property
    def balance_due(self):
        return max(self.total_amount - self.amount_paid, Decimal("0.00"))

    def update_payment_status(self):
        paid = self.amount_paid
        if paid <= 0:
            self.status = "sent" if self.invoice_sent else "draft"
        elif paid < self.total_amount:
            self.status = "partial"
        else:
            self.status = "paid"

        if self.status != "paid" and self.due_date < timezone.now().date():
            self.status = "overdue"

        super(ProjectPaymentInvoice, self).save(update_fields=["status"])

    
    
    def __str__(self):
        return f"{self.invoice_no} - {self.project.name}"



class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"          
    CONFIRMED = "confirmed", "Confirmed"   
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"    

class PaymentMethod(models.TextChoices):
    BANK_TRANSFER = "bank_transfer", "Bank Transfer"
    CASH = "cash", "Cash"
    JAZZCASH = "jazzcash", "JazzCash"
    EASYPAISA = "easypaisa", "EasyPaisa"
    CHEQUE = "cheque", "Cheque"
    OTHER = "other", "Other"




class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="payments")
    invoice = models.ForeignKey(
    "ProjectPaymentInvoice",
    on_delete=models.CASCADE,
    related_name="payments",
    null=True,    
    blank=True   
)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=20,choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices,default=PaymentMethod.CASH )
    transaction_ref = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="received_payments")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
     if not self.invoice:
        return

     if self.status == PaymentStatus.CONFIRMED:
        confirmed_total = self.invoice.payments.filter(
            status=PaymentStatus.CONFIRMED
        ).exclude(pk=self.pk).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0.00")

        if confirmed_total + self.amount > self.invoice.total_amount:
            raise ValidationError("Payment cannot exceed invoice balance.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.invoice.update_payment_status()

    def __str__(self):
        return f"{self.invoice.invoice_no} - {self.amount} ({self.status})"