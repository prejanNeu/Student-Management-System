from django.db import models
from django.conf import settings 
from django.utils import timezone
from account.models import ClassLevel, Subject 
from datetime import timedelta 


def default_deadline():
    return timezone.now().date() + timedelta(days=7)


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    assignment = models.TextField()
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    classlevel = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, null=True, blank=True)
    deadline = models.DateField(default=default_deadline)
    created_at = models.DateTimeField(auto_now_add=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.title} - Due by {self.deadline}"