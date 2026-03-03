from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.shortcuts import redirect, render


def landing_view(request):
    return render(request, "landing.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")



@login_required(login_url="login")
@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")


# @login_required(login_url="login")
# def dashboard_view(request):
#     # Example static values for testing
#     total_revenue = 125000.50
#     total_expenses = 43000.75
#     paid_invoices_count = 42
#     overdue_count = 3

#     recent_invoices = [
#         {
#             "pk": 1,
#             "number": "INV-001",
#             "client_name": "Client A",
#             "amount": 1500.00,
#             "due_date": date(2026, 2, 10),
#             "status": "paid",
#         },
#         {
#             "pk": 2,
#             "number": "INV-002",
#             "client_name": "Client B",
#             "amount": 2500.00,
#             "due_date": date(2026, 2, 12),
#             "status": "overdue",
#         },
#     ]

#     projects_budget = [
#         {"name": "Website Redesign", "spent": 8000, "budget": 10000, "spent_pct": 80},
#         {"name": "Mobile App", "spent": 5000, "budget": 15000, "spent_pct": 33},
#     ]

#     context = {
#         "total_revenue": total_revenue,
#         "total_expenses": total_expenses,
#         "paid_invoices_count": paid_invoices_count,
#         "overdue_count": overdue_count,
#         "recent_invoices": recent_invoices,
#         "projects_budget": projects_budget,
#     }

#     return render(request, "dashboard.html", context)



@login_required(login_url="login")
def dashboard_view(request):
    company = request.user.company
    active_employees = company.employees.filter(is_active=True)
    active_projects = company.projects.filter(status="active")

    context = {
        "company": company,
        "active_employees": active_employees,
        "active_employees_count": active_employees.count(),
        "active_projects": active_projects,
        "active_projects_count": active_projects.count(),
    }
    return render(request, "dashboard.html", context)