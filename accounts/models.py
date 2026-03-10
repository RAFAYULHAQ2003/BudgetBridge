import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.contrib.auth.models import Permission



class User(AbstractUser):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    company = models.ForeignKey(
        "operations.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_users",
    )


    
    def __str__(self):
        return self.email


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)  
    description = models.TextField(blank=True)
    company = models.ForeignKey(
        "operations.Company",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="roles",
    )
    permissions = models.ManyToManyField(Permission, blank=True)

    class Meta:
        unique_together = ("name", "company")

    def clean(self):
        if not self.name:
            raise ValidationError("Role name is required.")
        if not self.company:
            raise ValidationError("Role must be associated with a company.")
        super().clean()

    def get_or_create_permission_group(self):
        group_name = f"{slugify(self.name)}_{slugify(self.company.name)}"
        group, created = Group.objects.get_or_create(name=group_name)
        group.permissions.set(self.permissions.all())
        group.save()

        return group

    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)  

    @property
    def group(self):
        group_name = f"{slugify(self.name)}_{slugify(self.company.name)}"
        return Group.objects.get(name=group_name)

    def __str__(self):
        return f"{self.name} ({self.company.name})"