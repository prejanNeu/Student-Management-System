from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, role='student', password=None, **extra_fields):
        if not email:
            raise ValueError('Email must be provided')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        user = self.create_user(email, full_name, role='admin', password=password, **extra_fields)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    
class UserPhoto(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name="photo")
    user_image = models.ImageField(upload_to="userImage/", blank=True, null=True)

    def __str__(self):
        
        return f"{self.user.full_name} Photo"
    
    
class StudentClass(models.Model) :
    
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,related_name="user_class")
    std_class = models.IntegerField()
    
    def __str__(self):
        return f"{self.user.full_name} in class {self.std_class}"