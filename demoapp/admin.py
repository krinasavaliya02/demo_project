from django.contrib import admin
from .models import Project, Company

# Register your models here.
admin.site.register(Company)
admin.site.register(Project)