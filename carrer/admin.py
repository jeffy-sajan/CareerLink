from django.contrib import admin
from .models import JobSeekerProfile, EmployerProfile, Job, JobApplication

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'resume')
    search_fields = ('user__username', 'user__email', 'phone')

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'phone')
    search_fields = ('user__username', 'user__email', 'company_name')


admin.site.register(Job)
admin.site.register(JobApplication)