from django.urls import path
from .views import CompanyExpenseCreateView, CompanyExpenseListView, ExpenseCreateView, ExpenseListView, ExpenseApprovalListView, ExpenseApprovalUpdateView, PaymentCreateView,ProjectPaymentInvoiceCreateView, ProjectPaymentInvoiceListView, report_view, ProjectInvoiceListView, company_invoices_view, select_project_invoices,CompanyExpenseApprovalListView, CompanyExpenseApprovalUpdateView, CompanyExpenseAccountantListView, ExpenseInvoiceView, ExpenseInvoiceDownloadView
from . import views
urlpatterns = [
    path("expenses/", ExpenseListView.as_view(), name="expense-list"),
    path("expenses/add/", ExpenseCreateView.as_view(), name="expense-add"),
    path("expenses/approve/", ExpenseApprovalListView.as_view(), name="expense_approval_list"),
    path("expenses/approve/<uuid:pk>/", ExpenseApprovalUpdateView.as_view(), name="expense_approval_update"),
    path("report/", views.report_view, name="report"),
    path("company/<uuid:company_id>/invoices/", views.company_invoices_view, name="company_invoices"),
    path("company/<uuid:company_id>/invoices/", views.company_invoices_view, name="company_invoices"),
    path("company/<uuid:company_id>/invoices/select-project/", views.select_project_invoices, name="select_project_invoices"),
    path("company-expense/add/", CompanyExpenseCreateView.as_view(), name="company-expense-add"),
    path("company-expense/", CompanyExpenseListView.as_view(), name="company-expense-list"),
    path(
        "company-expense/approve/",
        CompanyExpenseApprovalListView.as_view(),
        name="company-expense-approval-list",
    ),
    path(
        "company-expense/approve/<uuid:pk>/",
        CompanyExpenseApprovalUpdateView.as_view(),
        name="company-expense-approve",
    ),
   
    path(
        "accountant/expenses/",
        views.CompanyExpenseAccountantListView.as_view(),
        name="accountant-expense-list",
    ),

   
    path(
        "accountant/expense/<uuid:expense_id>/invoice/",
        views.ExpenseInvoiceView.as_view(),
        name="expense-invoice-view",
    ),

    
    path(
        "accountant/expense/<uuid:expense_id>/invoice/generate/",
        views.ExpenseInvoiceDownloadView.as_view(),
        name="expense-invoice-download",
    ),

    path("project-payments/", ProjectPaymentInvoiceListView.as_view(), name="project-payment-invoice-list"),
    path("project-payments/add/", ProjectPaymentInvoiceCreateView.as_view(), name="project-payment-invoice-add"),
    path("project-payments/<uuid:pk>/payment/", PaymentCreateView.as_view(), name="project-payment-add"),
    path(
        "project-payment-invoice/<uuid:invoice_id>/payments/",
        views.project_invoice_payments,
        name="project-invoice-payments"
    ),

]