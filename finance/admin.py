from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import ExpenseCategory, Expense, Invoice, InvoiceItem, Payment
from operations.models import Company, Client, Project
from workforce.models import EmployeeProfile




class BaseCompanyAdmin(admin.ModelAdmin):
   

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.company = request.user.company
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser and "company" in fields:
            fields = [f for f in fields if f != "company"]
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
       
        if not request.user.is_superuser:
            if db_field.name == "company":
                kwargs["queryset"] = Company.objects.filter(id=request.user.company.id)

            if db_field.name == "project":
                kwargs["queryset"] = Project.objects.filter(company=request.user.company)

            if db_field.name == "client":
                kwargs["queryset"] = Client.objects.filter(company=request.user.company)

            if db_field.name == "employee":
                kwargs["queryset"] = EmployeeProfile.objects.filter(company=request.user.company)

            if db_field.name == "invoice":
                kwargs["queryset"] = Invoice.objects.filter(company=request.user.company)

            if db_field.name == "category":
                kwargs["queryset"] = ExpenseCategory.objects.filter(company=request.user.company)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)




@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(BaseCompanyAdmin):
    list_display = ("name", "company", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)




@admin.register(Expense)
class ExpenseAdmin(BaseCompanyAdmin):
    list_display = (
        "employee",
        "project",
        "category",
        "amount",
        "status",
        "expense_date",
    )
    list_filter = ("status", "category")
    search_fields = ("employee__user__email", "project__name")
    readonly_fields = ("created_at",)
    ordering = ("-expense_date",)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = ("total",)




class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ("created_at",)




@admin.register(Invoice)
class InvoiceAdmin(BaseCompanyAdmin):
    list_display = (
        "invoice_no",
        "client",
        "project",
        "status",
        "total_amount",
        "issue_date",
        "due_date",
    )
    list_filter = ("status",)
    search_fields = ("invoice_no", "client__name")
    readonly_fields = ("subtotal", "tax_amount", "total_amount", "created_at")
    inlines = [InvoiceItemInline, PaymentInline]
    ordering = ("-issue_date",)




@admin.register(Payment)
class PaymentAdmin(BaseCompanyAdmin):
    list_display = (
        "invoice",
        "amount",
        "status",
        "payment_method",
        "paid_at",
    )
    list_filter = ("status", "payment_method")
    search_fields = ("invoice__invoice_no", "transaction_ref")
    readonly_fields = ("created_at",)
    ordering = ("-paid_at",)