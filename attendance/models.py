from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
User = get_user_model()


class Attendance(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        
        return f"{self.user.full_name} on date {self.date}"
