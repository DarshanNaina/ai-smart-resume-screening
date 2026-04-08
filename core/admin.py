from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Application, Interview, Job, OTPCode, Organization, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (("Role", {"fields": ("role", "organization")}),)


admin.site.register(Organization)
admin.site.register(Job)
admin.site.register(Application)
admin.site.register(Interview)
admin.site.register(OTPCode)
