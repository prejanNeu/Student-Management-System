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
    
    
   
class Subject(models.Model):
    name = models.CharField(max_length=55, unique=True)

    def __str__(self):
        return self.name


class ClassLevel(models.Model):

    level = models.PositiveIntegerField(unique=True, verbose_name=("Class Level"))

    def __str__(self):
        return f"Class {self.level}"


class ClassSubject(models.Model):

    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('class_level', 'subject')

    def __str__(self):
        return f"{self.class_level} - {self.subject}"


class StudentClassEnrollment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="class_enrollments")
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    is_current = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'class_level')

    def __str__(self):
        status = "Current" if self.is_current else "Past"
        return f"{self.student} in {self.class_level} ({status})"
