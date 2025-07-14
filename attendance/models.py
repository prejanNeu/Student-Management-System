from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from account.models import ClassLevel
from django.utils import timezone


User = get_user_model()



class Attendance(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    classlevel = models.ForeignKey(ClassLevel,on_delete=models.DO_NOTHING,null=True,blank=True)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=55, default="present")

    class Meta:
        unique_together = ('student', 'classlevel', 'date')
    
    def __str__(self):
        return f"{self.student.full_name} {self.classlevel.level}on date {self.date}"
    
