from django.urls import path
from .views import CompanyProjectListView, ProjectDetailView

urlpatterns = [
    path(
        "company/<uuid:pk>/projects/",
        CompanyProjectListView.as_view(),
        name="company_projects",
    ),
    path(
        "project/<uuid:pk>/",
        ProjectDetailView.as_view(),
        name="project_detail",
    ),
]
