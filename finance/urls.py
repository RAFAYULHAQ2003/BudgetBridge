from django.urls import path
from .views import ExpenseCreateView, ExpenseListView, ExpenseApprovalListView, ExpenseApprovalUpdateView, report_view, ProjectInvoiceListView, company_invoices_view, select_project_invoices
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

]