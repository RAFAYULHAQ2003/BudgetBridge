import uuid
from django.db import models
from enum import StrEnum



class ProjectStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    registration_no = models.CharField(max_length=100,unique=True)
    tax_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.TextField()
    country = models.CharField(max_length=100)
    currency = models.CharField(max_length=3)  
    account_no = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="clients",
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    project_manager = models.ForeignKey(
        "workforce.EmployeeProfile",
        on_delete=models.SET_NULL,
        null=True,
        related_name="managed_projects",
    )
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.value) for s in ProjectStatus],
        default=ProjectStatus.PLANNED.value,
    )
    def __str__(self):
        return self.name



class EmployeeProject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        "workforce.EmployeeProfile",
        on_delete=models.CASCADE,
        related_name="project_assignments",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="employee_assignments",
    )
    role_in_project = models.CharField(max_length=100)

    class Meta:
        unique_together = ("employee", "project")

    def __str__(self):
        return f"{self.employee} → {self.project}"
