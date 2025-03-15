from django.db import models
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static

# ✅ Custom User Model
class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)  # Optional user bio
    profile_image = models.ImageField(
        upload_to="profile_pics/",
        blank=True,
        null=True
    )  
    invite_code = models.CharField(max_length=10, blank=True, null=True)  # Invite code for access control

    def __str__(self):
        return self.username

    # ✅ Function to get profile image or default
    def get_profile_image(self):
        if self.profile_image:
            return self.profile_image.url
        return static("profile_pics/default_profile.png")  # ✅ Default profile picture


# ✅ Post Model (Interactive Feed)
class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')  # Link post to user
    content = models.TextField()  # Post content (text)
    created_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp
    likes = models.ManyToManyField(CustomUser, related_name='liked_posts', blank=True)  # Many users can like a post

    class Meta:
        ordering = ['-created_at']  # Ensure newest posts show first

    def total_likes(self):
        return self.likes.count()  # Count total likes

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"  # Show first 30 chars of post


# ✅ Comment Model (For Posts)
class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')  # User who commented
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')  # Link comment to post
    content = models.TextField()  # Comment text
    created_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp

    class Meta:
        ordering = ['-created_at']  # Ensure newest comments show first

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"


# ✅ Private Message Model (DMs)
class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_messages")  # Who sent the message
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_messages")  # Who received it
    content = models.TextField()  # Message text
    created_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp
    is_read = models.BooleanField(default=False)  # Track if the message is read

    class Meta:
        ordering = ['-created_at']  # Show latest messages first

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


