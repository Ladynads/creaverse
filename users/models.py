from django.contrib.auth.models import AbstractUser
from django.db import models

# Custom User Model
class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    invite_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.username

# Post Model for the Interactive Feed
class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Links post to user
    content = models.TextField()  # Post content (text)
    created_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"  # Show first 30 chars of post
