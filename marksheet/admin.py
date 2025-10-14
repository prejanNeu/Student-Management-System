from django.contrib import admin
from .models import ExamType, Marksheet, ClassParticipation


admin.site.register(ExamType)
admin.site.register(Marksheet)
admin.site.register(ClassParticipation)