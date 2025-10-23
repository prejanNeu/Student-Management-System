# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, ClassLevel, StudentClassEnrollment, Subject, ClassSubject # your user model
from .forms import CustomUserCreationForm


class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm  # ✅ use your form here
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2', "gender"),
        }),
    )
    list_display = ('id','email', 'full_name', 'role', 'is_active', 'is_staff')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'full_name', 'role', 'password', "gender")}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    filter_horizontal = ()

admin.site.register(CustomUser, CustomUserAdmin)


admin.site.register(ClassLevel)
admin.site.register(StudentClassEnrollment)
admin.site.register(Subject)
admin.site.register(ClassSubject)
# Register your models here.
