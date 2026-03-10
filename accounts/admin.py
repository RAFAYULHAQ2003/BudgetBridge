from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.text import slugify
from django.contrib.auth.models import Group
from .models import User, Role
from django.contrib.auth.models import Permission


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("username","email", "company", "is_staff", "is_active", "is_superuser")
    list_filter = ("company", "is_staff", "is_superuser")
    search_fields = ("email", "username", "first_name", "last_name")
    readonly_fields = ("created_by",)

    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username","email", "password1", "password2","first_name", "last_name", "company", "groups"),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)

   

  
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            if "company" in form.base_fields:
                form.base_fields["company"].widget = forms.HiddenInput()
        return form

    
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.company = request.user.company

        if not change:
            obj.created_by = request.user

        obj.is_staff = True
        super().save_model(request, obj, form, change)


    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "groups" and not request.user.is_superuser:
            company_slug = slugify(request.user.company.name)
            kwargs["queryset"] = Group.objects.filter(name__endswith=f"_{company_slug}")
        return super().formfield_for_manytomany(db_field, request, **kwargs)




@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "company")
    search_fields = ("name", "company__name")
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("name", "company", "permissions"),
        }),
    )

    filter_horizontal = ("permissions",) 

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.get_or_create_permission_group()  
        form.save()  

