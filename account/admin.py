from django.contrib import admin
from .models import ClassLevel, StudentClassEnrollment, Subject, ClassSubject, CustomUser


admin.site.register(ClassLevel)
admin.site.register(StudentClassEnrollment)
admin.site.register(Subject)
admin.site.register(ClassSubject)
admin.site.register(CustomUser)
# Register your models here.
