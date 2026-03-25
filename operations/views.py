from multiprocessing import context

from django.views.generic import DetailView, CreateView
from .forms import ProjectWithClientForm
from operations.models import Client
from django.shortcuts import get_object_or_404, redirect
from .models import Company, Project
from finance.models import Expense
from django.db.models import Sum
from .forms import EmployeeProjectForm

class CompanyProjectListView(DetailView):
    model = Company
    template_name = "operations/company_projects.html"
    context_object_name = "company"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects"] = self.object.projects.select_related(
            "project_manager", "client"
        ).prefetch_related("employee_assignments__employee")
        return context


# class ProjectDetailView(DetailView):
#     model = Project
#     template_name = "operations/project_detail.html"

#     context_object_name = "project"

#     def get_queryset(self):
#         return Project.objects.select_related(
#             "company", "project_manager", "client"
#         ).prefetch_related("employee_assignments__employee")

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         project = self.object

       
#         total_approved_expenses = Expense.objects.filter(
#             project=project,
#             status="approved"  
#         ).aggregate(total=Sum('amount'))['total'] or 0

#         context['total_approved_expenses'] = total_approved_expenses

       
#         if project.budget and project.budget != 0:
#             profit_loss_percentage = ((project.budget - total_approved_expenses) / project.budget) * 100
#         else:
#             profit_loss_percentage = 0

#         context['profit_loss_percentage'] = round(profit_loss_percentage, 2)
#         return context





class ProjectDetailView(DetailView):
    model = Project
    template_name = "operations/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.select_related(
            "company", "project_manager", "client"
        ).prefetch_related("employee_assignments__employee")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

        # Expense info
        total_approved_expenses = Expense.objects.filter(
            project=project,
            status="approved"
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['total_approved_expenses'] = total_approved_expenses

        if project.budget and project.budget != 0:
            profit_loss_percentage = ((project.budget - total_approved_expenses) / project.budget) * 100
        else:
            profit_loss_percentage = 0
        context['profit_loss_percentage'] = round(profit_loss_percentage, 2)

        # EmployeeProject form
        context['employee_project_form'] = EmployeeProjectForm(company=project.company)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EmployeeProjectForm(request.POST, company=self.object.company)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.project = self.object
            assignment.save()
            return redirect('project_detail', pk=self.object.pk)
        context = self.get_context_data()
        context['employee_project_form'] = form
        return self.render_to_response(context)    

class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectWithClientForm
    template_name = "operations/project_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # pass user to form
        return kwargs
    
    def get_context_data(self, **kwargs):
     context = super().get_context_data(**kwargs)
     context['company'] = self.request.user.employee_profile.company
     return context

    def form_valid(self, form):
        # Create the client first
        client = Client.objects.create(
            company=self.request.user.employee_profile.company,
            name=form.cleaned_data['client_name'],
            email=form.cleaned_data['client_email'],
            phone=form.cleaned_data['client_phone'],
            address=form.cleaned_data['client_address'],
        )

        # Now create the project
        project = form.save(commit=False)
        project.company = self.request.user.employee_profile.company
        project.client = client
        project.save()

        return redirect('company_projects', pk=project.company.id)