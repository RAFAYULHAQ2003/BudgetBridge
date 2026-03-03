from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib import messages
from decimal import Decimal
from django.views.generic import UpdateView
from .models import Expense, Invoice, InvoiceItem
from .forms import ExpenseForm
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.db.models import Sum, F
from datetime import date, timedelta
from operations.models import Company
from finance.models import Invoice, Expense
from operations.models import Project
from workforce.models import EmployeeProfile
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .tasks import send_invoice_email

class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "finance/expense_form.html"
    success_url = reverse_lazy("expense-list")


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  
        return kwargs

    def form_valid(self, form):
        expense = form.save(commit=False)

        
        expense.company = self.request.user.company
        expense.employee = self.request.user.employee_profile
        expense.save()

        
        if expense.project and expense.project.client:
            invoice = Invoice.objects.create(
                company=expense.company,
                client=expense.project.client,
                project=expense.project,
                invoice_no=f"INV-{timezone.now().timestamp()}",
                issue_date=timezone.now().date(),
                due_date=timezone.now().date(),
                subtotal=expense.amount,
                created_by=self.request.user,
            )

            invoice.calculate_totals()
            invoice.save()

           
            InvoiceItem.objects.create(
                invoice=invoice,
                description=expense.description or "Project Expense",
                quantity=1,
                unit_price=expense.amount,
            )

            

        messages.success(self.request, "Expense added and invoice generated.")
        return super().form_valid(form)
    
class ExpenseListView(ListView):
    model = Expense
    template_name = "finance/expense_list.html"
    context_object_name = "expenses"

    def get_queryset(self):
        return Expense.objects.filter(
            company=self.request.user.company
        ).select_related("employee", "project", "category")
    


from .models import Expense, ExpenseStatus

class ExpenseApprovalListView(ListView):
    model = Expense
    template_name = "finance/expense_approval_list.html"
    context_object_name = "expenses"

    def get_queryset(self):
        
        return Expense.objects.filter(
            project__project_manager=self.request.user.employee_profile,
            status=ExpenseStatus.SUBMITTED
        ).select_related("employee", "project", "category")



# class ExpenseApprovalUpdateView(UpdateView):
#     model = Expense
#     fields = ["status"]
#     template_name = "finance/expense_approval_update.html"
#     success_url = reverse_lazy("expense_approval_list")

#     def form_valid(self, form):
#         expense = form.save(commit=False)
#         expense.approved_by = self.request.user
#         expense.approved_at = timezone.now()
#         expense.save()

#         # Send invoice email if approved
#         if expense.status == ExpenseStatus.APPROVED and expense.project.client.email:
#             # Get the invoice linked to this expense's project
#             invoice = Invoice.objects.filter(project=expense.project).last()
#             if invoice:
#                 # Render HTML email
#                 html_content = render_to_string("finance/email_invoice.html", {
#                     "invoice": invoice,
#                     "invoice_items": invoice.items.all(),  # assuming related_name="items"
#                     "company": expense.company,
#                     "client": expense.project.client,
#                 })

#                 subject = f"Invoice #{invoice.invoice_no} for Project: {expense.project.name}"
#                 from_email = "noreply@budgetbridge.com"
#                 to_email = [expense.project.client.email]

#                 email = EmailMultiAlternatives(subject, "", from_email, to_email)
#                 email.attach_alternative(html_content, "text/html")
#                 email.send(fail_silently=True)

#         messages.success(self.request, f"Expense {expense.status} successfully.")
#         return super().form_valid(form)


class ExpenseApprovalUpdateView(UpdateView):
    model = Expense
    fields = ["status"]
    template_name = "finance/expense_approval_update.html"
    success_url = reverse_lazy("expense_approval_list")

    def form_valid(self, form):
        expense = form.save(commit=False)
        expense.approved_by = self.request.user
        expense.approved_at = timezone.now()
        expense.save()

       
        if expense.status == ExpenseStatus.APPROVED and expense.project.client.email:
            invoice = Invoice.objects.create(
                company=expense.company,
                client=expense.project.client,
                project=expense.project,
                invoice_no=f"INV-{timezone.now().timestamp()}",
                issue_date=timezone.now().date(),
                due_date=timezone.now().date(),
                subtotal=expense.amount,
                created_by=self.request.user,
            )

           
            InvoiceItem.objects.create(
                invoice=invoice,
                description=expense.description or "Project Expense",
                quantity=1,
                unit_price=expense.amount,
            )

           
            invoice.calculate_totals()
            invoice.save()

           
            send_invoice_email.delay(invoice.id)

        messages.success(self.request, f"Expense {expense.status} successfully.")
        return super().form_valid(form)

def report_view(request):
    """
    Single page dashboard for Budget Control & Reporting
    """

    # --- Financial KPIs ---
    total_revenue = Invoice.objects.filter(status__in=["paid", "partial"]).aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    total_expenses = Expense.objects.aggregate(total=Sum("amount"))["total"] or 0

    paid_invoices_count = Invoice.objects.filter(status="paid").count()
    overdue_count = Invoice.objects.filter(status="overdue").count()

    # --- Project Budgets ---
    projects = Project.objects.all()
    projects_budget = []
    for project in projects:
        spent = Expense.objects.filter(project=project).aggregate(total=Sum("amount"))["total"] or 0
        budget = project.budget or 0
        spent_pct = int((spent / budget) * 100) if budget > 0 else 0
        projects_budget.append({
            "name": project.name,
            "spent": spent,
            "budget": budget,
            "spent_pct": spent_pct,
        })

    
    recent_invoices_qs = Invoice.objects.order_by("-issue_date")[:5]
    recent_invoices = []
    for inv in recent_invoices_qs:
        recent_invoices.append({
            "number": inv.invoice_no,
            "client_name": inv.client.name if inv.client else "-",
            "amount": inv.total_amount,
            "status": inv.get_status_display(),
            "issue_date": inv.issue_date,
        })

    context = {
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "paid_invoices_count": paid_invoices_count,
        "overdue_count": overdue_count,
        "projects_budget": projects_budget,
        "recent_invoices": recent_invoices,
    }

    return render(request, "finance/report.html", context)



def company_invoices_view(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    project_id = request.GET.get("project")  # optional filter
    projects = company.projects.all()

    if project_id:
        invoices = Invoice.objects.filter(company=company, project_id=project_id)
    else:
        invoices = Invoice.objects.filter(company=company)

    context = {
        "company": company,
        "projects": projects,
        "invoices": invoices,
        "selected_project_id": project_id or "",
    }
    return render(request, "finance/invoice_list.html", context)


def select_project_invoices(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    projects = Project.objects.filter(company=company)
    context = {
        "company": company,
        "projects": projects,
    }
    return render(request, "finance/select_project.html", context)

class ProjectInvoiceListView(ListView):
    model = Invoice
    template_name = "finance/invoice_list.html"
    context_object_name = "invoices"

    def get_queryset(self):
        company_id = self.kwargs.get("company_id")
        project_id = self.kwargs.get("project_id", None)

        qs = Invoice.objects.filter(company_id=company_id)
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs.order_by("-issue_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_id = self.kwargs.get("company_id")
        context["company"] = get_object_or_404(Project, company_id=company_id).company
        context["projects"] = Project.objects.filter(company_id=company_id)

        # Keep track of selected project
        context["selected_project_id"] = self.kwargs.get("project_id", "")

        return context
    