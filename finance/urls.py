from django.urls import path
from .views import CompanyExpenseCreateView, CompanyExpenseListView, ExpenseCreateView, ExpenseListView, ExpenseApprovalListView, ExpenseApprovalUpdateView, report_view, ProjectInvoiceListView, company_invoices_view, select_project_invoices,CompanyExpenseApprovalListView, CompanyExpenseApprovalUpdateView
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

]