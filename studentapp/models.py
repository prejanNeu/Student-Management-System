from django.db import models
from django.conf import settings 
from django.contrib.auth.models import User 
from django.core.validators import MinValueValidator,MaxValueValidator


class Student(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,null=True, blank=True)
    date_of_birth = models.DateField(null=True,blank=True)
    father_name = models.CharField(max_length=55, null=True, blank=True)
    image = models.ImageField(upload_to='student/',null=True,blank=True)
    
    