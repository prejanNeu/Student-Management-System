from django.conf import settings
from django.db import models
from django.utils import timezone
from account.models import ClassLevel, Subject

class ExamType(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class Marksheet(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    classlevel = models.ForeignKey(
        ClassLevel, on_delete=models.DO_NOTHING, blank=True, null=True
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.SET_NULL, blank=True, null=True
    )
    full_marks = models.DecimalField(max_digits=5, decimal_places=2)
    marks = models.DecimalField(max_digits=5, decimal_places=2)

    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.marks}/{self.full_marks})"
