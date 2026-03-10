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