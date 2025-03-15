from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

# Custom User Model
class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)  # Optional user bio
    profile_image = models.ImageField(upload_to="profile_pics/", blank=True, null=True)  # Profile picture
    invite_code = models.CharField(max_length=10, blank=True, null=True)  # Invite code for access control

    def __str__(self):
        return self.username


# Post Model (Interactive Feed)
class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Link post to user
    content = models.TextField()  # Post content (text)
    created_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp
    likes = models.ManyToManyField(CustomUser, related_name='liked_posts', blank=True)  # Many users can like a post

    def total_likes(self):
        return self.likes.count()  # Count total likes

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"  # Show first 30 chars of post


# Comment Model (For Posts)
class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # User who commented
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')  # Link comment to post
    content = models.TextField()  # Comment text
    created_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"
