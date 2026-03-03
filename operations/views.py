from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from .models import Company, Project


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


class ProjectDetailView(DetailView):
    model = Project
    template_name = "operations/project_detail.html"

    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.select_related(
            "company", "project_manager", "client"
        ).prefetch_related("employee_assignments__employee")
