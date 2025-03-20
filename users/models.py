import random
import string
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static
from django.utils.timezone import now
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# ✅ Manually download required NLTK data files
# Run in terminal: `python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"`

# ✅ Function to generate unique invite codes
def generate_invite_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


# ✅ Custom User Model (Includes Invite System)
class CustomUser(AbstractUser):
    """Extends Django's AbstractUser with additional fields."""
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    used_invite = models.BooleanField(default=False)  # Tracks if user registered with an invite

    def __str__(self):
        return self.username

    def get_profile_image(self):
        """Returns the user's profile image or the default avatar if none is set."""
        if self.profile_image and hasattr(self.profile_image, "url"):
            return self.profile_image.url  # Use uploaded image
        return static("profile_pics/default_profile.webp")  # Serve default avatar


# ✅ Invite Code Model (For Invite-Only Registration)
class InviteCode(models.Model):
    """Model to manage invite codes for user registration."""
    code = models.CharField(max_length=10, unique=True, default=generate_invite_code)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="generated_invites")
    used_by = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="invite_used_by")
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def mark_used(self, user):
        """Mark invite code as used."""
        self.used_by = user
        self.used_at = now()
        self.save()

    def __str__(self):
        return f"Invite {self.code} - {'Used' if self.used_by else 'Unused'}"


# ✅ Comment Model (For Posts)
class Comment(models.Model):
    """Comments on posts, linked to user & post."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey("feed.Post", on_delete=models.CASCADE, related_name="comments")  # ✅ String reference to avoid circular import
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"


# ✅ Private Message Model (DMs)
class Message(models.Model):
    """Direct messages between users."""
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# ✅ User Interaction Model (Tracks User Engagement)
class UserInteraction(models.Model):
    """Tracks user engagement with posts (likes, comments, views)."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_interactions")
    post = models.ForeignKey("feed.Post", on_delete=models.CASCADE, related_name="post_interactions")  # ✅ String reference
    liked = models.BooleanField(default=False)
    commented = models.BooleanField(default=False)
    viewed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.post.id} ({'Liked' if self.liked else ''} {'Commented' if self.commented else ''})"

