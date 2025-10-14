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


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignment_submissions')
    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student.full_name} - {self.assignment.title} - {self.marks}"