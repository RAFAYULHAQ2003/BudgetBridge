from urllib import request

from django.views.generic import CreateView, ListView, DetailView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib import messages
from decimal import Decimal
from django.views.generic import UpdateView
from .models import Expense, Invoice, InvoiceItem, InvoiceStatus
from .forms import ExpenseForm, CompanyExpenseForm
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.db.models import Sum, F
from datetime import date, timedelta
from operations.models import Company
from finance.models import Invoice, Expense
from operations.models import Project
from workforce.models import EmployeeProfile
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .tasks import send_invoice_email, send_payment_invoice_email
from .models import Expense, ExpenseStatus
from weasyprint import HTML
from django.http import Http404, HttpResponse
from django.template.loader import render_to_string
from .models import Payment, PaymentStatus, PaymentMethod, ProjectPaymentInvoice
from .forms import ProjectPaymentInvoiceForm, PaymentForm


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

     
        messages.success(self.request, "Expense submitted successfully.")
        return super().form_valid(form) 
    

class ExpenseListView(ListView):
    model = Expense
    template_name = "finance/expense_list.html"
    context_object_name = "expenses"

    def get_queryset(self):
        return Expense.objects.filter(
            company=self.request.user.company,
        ).exclude(
            project__isnull=True
        ).select_related("employee", "project", "category")
    




class ExpenseApprovalListView(ListView):
    model = Expense
    template_name = "finance/expense_approval_list.html"
    context_object_name = "expenses"

    def get_queryset(self):
        
        return Expense.objects.filter(
            project__project_manager=self.request.user.employee_profile,
            status=ExpenseStatus.SUBMITTED
        ).select_related("employee", "project", "category")




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
                expense=expense,
                invoice_no=f"INV-{timezone.now().timestamp()}",
                issue_date=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=5),
                subtotal=expense.amount,
                created_by=self.request.user,
                status=InvoiceStatus.SENT,
            )

           
            InvoiceItem.objects.create(
                invoice=invoice,
                description=expense.description or "Project Expense",
                category=expense.category.name if expense.category else " ",
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

  
    total_revenue = Invoice.objects.filter(status__in=["paid", "partial"]).aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    total_expenses = Expense.objects.aggregate(total=Sum("amount"))["total"] or 0

    paid_invoices_count = Invoice.objects.filter(status="paid").count()
    overdue_count = Invoice.objects.filter(status="overdue").count()

    
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
    project_id = request.GET.get("project") 
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
        context["selected_project_id"] = self.kwargs.get("project_id", "")

        return context



class CompanyExpenseCreateView(CreateView):
    model = Expense
    form_class = CompanyExpenseForm
    template_name = "finance/company_expense_form.html"
    success_url = reverse_lazy("company-expense-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        expense = form.save(commit=False)
        expense.company = self.request.user.company
        expense.employee = self.request.user.employee_profile
        expense.save()

       
        messages.success(self.request, "Company expense submitted successfully.")
        return super().form_valid(form)
    



class CompanyExpenseListView(ListView):
    model = Expense
    template_name = "finance/company_expense_list.html"
    context_object_name = "expenses"

    def get_queryset(self):
        return Expense.objects.filter(
            company=self.request.user.company,
            project__isnull=True
        ).select_related("employee", "category").order_by("-expense_date")
    

class CompanyExpenseApprovalListView(ListView):
    model = Expense
    template_name = "finance/company_expense_approval_list.html"
    context_object_name = "expenses"
   

    def get_queryset(self):
        return Expense.objects.filter(
            project__isnull=True, 
            status=ExpenseStatus.SUBMITTED
        ).select_related("employee", "category").order_by("-expense_date")
    
class CompanyExpenseApprovalUpdateView(UpdateView):
    model = Expense
    fields = ["status"]
    template_name = "finance/company_expense_approval_update.html"
    success_url = reverse_lazy("company-expense-approval-list")
    

    def form_valid(self, form):
        expense = form.save(commit=False)
        expense.approved_by = self.request.user
        expense.approved_at = timezone.now()
        expense.save()

     
        invoice = Invoice.objects.create(
            company=expense.company,
            expense=expense,
            client=None,
            project=None,
            invoice_no=f"COMP-{timezone.now().timestamp()}",
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=5),
            subtotal=expense.amount,
            created_by=self.request.user,
        )

        InvoiceItem.objects.create(
            invoice=invoice,
            description=expense.description or "Company Expense",
            category=expense.category.name if expense.category else "",
            quantity=1,
            unit_price=expense.amount,
        )

        invoice.calculate_totals()
        invoice.save()

        messages.success(self.request, f"Company Expense {expense.status} successfully.")
        return super().form_valid(form)


class CompanyExpenseAccountantListView(ListView):
    model = Expense
    template_name = "finance/company_expense_accountant_list.html"
    context_object_name = "expenses"

    def get_queryset(self):
        return Expense.objects.filter(
            company=self.request.user.company,
            status=ExpenseStatus.APPROVED
        ).select_related("employee", "category", "project").order_by("-expense_date")
    
class ExpenseInvoiceView(View):
    def get(self, request, expense_id):
        expense = get_object_or_404(Expense, id=expense_id, company=request.user.company)
       
        if expense.project:
            invoice = Invoice.objects.filter(company=expense.company, project=expense.project, subtotal=expense.amount).first()
        else:
            invoice = Invoice.objects.filter(company=expense.company, project=None, subtotal=expense.amount).first()

        html = render_to_string("finance/invoice_detail.html", {"expense": expense, "invoice": invoice})
        return HttpResponse(html)



class ExpenseInvoiceDownloadView(View):
   
    def get(self, request, expense_id):
        expense = get_object_or_404(Expense, id=expense_id, company=request.user.company)

       
        invoice = getattr(expense, "invoice", None)
        if not invoice:
            raise Http404("No invoice found for this expense.")
      
        html_string = render_to_string("finance/invoice_detail_download.html", {"expense": expense, "invoice": invoice})
        pdf_file = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="Invoice-{invoice.invoice_no}.pdf"'
        return response
    






class ProjectPaymentInvoiceListView(ListView):
    model = ProjectPaymentInvoice
    template_name = "finance/project_payment_invoice_list.html"
    context_object_name = "invoices"

    def get_queryset(self):
        return ProjectPaymentInvoice.objects.filter(
            company=self.request.user.company
        ).select_related("project").prefetch_related("payments")


class ProjectPaymentInvoiceCreateView(CreateView):
    model = ProjectPaymentInvoice
    form_class = ProjectPaymentInvoiceForm
    template_name = "finance/project_payment_invoice_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        invoice = form.save(commit=False)
        invoice.company = self.request.user.company
        invoice.created_by = self.request.user
        invoice.invoice_no = f"INV-{timezone.now().timestamp()}"
        invoice.issue_date = timezone.now().date()
        invoice.save()

       
        send_payment_invoice_email.delay(str(invoice.id))
        

        messages.success(self.request, "Project Payment Invoice created and emailed.")
        return redirect("project-payment-invoice-list")





class PaymentCreateView(View):
    template_name = "finance/payment_form.html"

    def get(self, request, pk):
        invoice = get_object_or_404(
            ProjectPaymentInvoice,
            id=pk,
            company=request.user.company
        )
        form = PaymentForm(invoice=invoice)
        return render(request, self.template_name, {
            "form": form,
            "invoice": invoice
        })

    def post(self, request, pk):
     invoice = get_object_or_404(
        ProjectPaymentInvoice,
        id=pk,
        company=request.user.company
     )
     form = PaymentForm(request.POST, invoice=invoice)

     form.instance.invoice = invoice
     form.instance.company = request.user.company

     if form.is_valid():
        payment = form.save(commit=False)
        payment.created_by = request.user
        payment.received_by = request.user

        if payment.status == PaymentStatus.CONFIRMED and not payment.paid_at:
            payment.paid_at = timezone.now()

        payment.save()

        messages.success(request, "Payment recorded successfully.")
        return redirect("project-payment-invoice-list")

     return render(request, self.template_name, {
        "form": form,
        "invoice": invoice
     })
    


def project_invoice_payments(request, invoice_id):
    invoice = get_object_or_404(ProjectPaymentInvoice, id=invoice_id)
    payments = invoice.payments.all().order_by("-paid_at")
    return render(
        request,
        "finance/project_invoice_payments.html",
        {"invoice": invoice, "payments": payments},
    )    