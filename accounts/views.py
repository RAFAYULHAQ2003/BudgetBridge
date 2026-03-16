from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import User

from django.contrib.auth.forms import AuthenticationForm


def landing_view(request):
    return render(request, "landing.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("dashboard")
    else:
        form = AuthenticationForm(request)

    return render(request, "login.html", {"form": form})




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

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "profile.html"

    def get_object(self):
        return self.request.user
