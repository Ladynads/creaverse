from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('creator', 'Creator')], default='creator')
    invite_code = models.CharField(max_length=10, unique=True, blank=True, null=True)  # New field

    def __str__(self):
        return self.username