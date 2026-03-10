from django.contrib import admin

from workforce.models import EmployeeProfile
from .models import Company, Client, Project, EmployeeProject

class BaseCompanyAdmin(admin.ModelAdmin):
    """
    Base logic used by Client, Project, etc.
    """
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)

    def save_model(self, request, obj, form, change):
      
        if not request.user.is_superuser:
            obj.company = request.user.company
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        """
        Hide the 'company' field for Company Admins so they can't 
        even try to change it. Superadmins still see it.
        """
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            return [f for f in fields if f != 'company']
        return fields

@admin.register(Client)
class ClientAdmin(BaseCompanyAdmin):
    list_display = ("name", "email", "phone", "company")
    search_fields = ("name", "email")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        If a field MUST show (like choosing a company for a Superadmin), 
        ensure it only shows the relevant one.
        """
        if db_field.name == "company" and not request.user.is_superuser:
           
            kwargs["queryset"] = Company.objects.filter(id=request.user.company.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Project)
class ProjectAdmin(BaseCompanyAdmin):
    list_display = ("name", "client", "status", "budget")
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # When adding a project, only show clients belonging to 'my' company
        if not request.user.is_superuser:
            if db_field.name == "client":
                kwargs["queryset"] = Client.objects.filter(company=request.user.company)
            if db_field.name == "project_manager":
                from workforce.models import EmployeeProfile
                kwargs["queryset"] = EmployeeProfile.objects.filter(company=request.user.company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "registration_no", "email")
    def has_module_permission(self, request):
        
        return request.user.is_superuser
    




@admin.register(EmployeeProject)
class EmployeeProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee",
        "project",
        "role_in_project",
    )
    list_filter = ("project",)
    search_fields = ("employee__user__username", "project__name")
    ordering = ("project", "employee")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
       
        if request.user.is_superuser:
            return qs
        
        return qs.filter(project__company=request.user.company)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        #
        if not request.user.is_superuser:
            if db_field.name == "employee":
                kwargs["queryset"] = EmployeeProfile.objects.filter(company=request.user.company)
            elif db_field.name == "project":
                kwargs["queryset"] = Project.objects.filter(company=request.user.company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)