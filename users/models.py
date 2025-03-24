import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static
from django.utils.timezone import now
from django.core.exceptions import ValidationError

# Function to generate unique invite codes
def generate_invite_code():
    """Generates an 8-character alphanumeric invite code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Custom user model with social features
class CustomUser(AbstractUser):
    """Extended user model with social features."""
    bio = models.TextField(blank=True, null=True, help_text="Tell others about yourself")
    profile_image = models.ImageField(
        upload_to="profile_pics/",
        blank=True,
        null=True,
        help_text="Upload a profile picture"
    )
    used_invite = models.BooleanField(
        default=False,
        help_text="Has this user used an invite code?"
    )
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True,
        help_text="Users this user is following"
    )

    def get_profile_image(self):
        """Returns the profile image URL or default if none exists."""
        if self.profile_image and hasattr(self.profile_image, "url"):
            return self.profile_image.url
        return static("profile_pics/default_profile.webp")

    def clean(self):
        """Add custom validation logic."""
        if self.bio and len(self.bio) > 500:
            raise ValidationError("Bio cannot exceed 500 characters")
        super().clean()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username

# Invite-only registration system
class InviteCode(models.Model):
    """System for invite-only registrations."""
    code = models.CharField(
        max_length=10,
        unique=True,
        default=generate_invite_code,
        help_text="Unique invite code"
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="generated_invites",
        help_text="User who created this invite"
    )
    used_by = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invite_used",
        help_text="User who redeemed this invite"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def mark_used(self, user):
        """Records when an invite code is used."""
        if self.used_by:
            raise ValidationError("This invite code has already been used")
        self.used_by = user
        self.used_at = now()
        self.save()

    def is_valid(self):
        """Check if the invite code is still usable."""
        return not bool(self.used_by)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Invite Code"
        verbose_name_plural = "Invite Codes"

    def __str__(self):
        status = "Used" if self.used_by else "Active"
        return f"Invite {self.code} ({status})"

# Comment Model (For Posts)
class Comment(models.Model):
    """Comments on posts, linked to user & post."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey("feed.Post", on_delete=models.CASCADE, related_name="comments")  
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"    

# Private messaging system
class Message(models.Model):
    """Private messaging system between users."""
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="received_messages"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def mark_as_read(self):
        """Mark message as read."""
        if not self.is_read:
            self.is_read = True
            self.save()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Private Message"
        verbose_name_plural = "Private Messages"

    def __str__(self):
        status = "Read" if self.is_read else "Unread"
        return f"Message #{self.id} ({status})"

# User interaction tracking
class UserInteraction(models.Model):
    INTERACTION_TYPES = [
        ('LIKE', 'Like'),
        ('COMMENT', 'Comment'),
        ('VIEW', 'View'),
        ('SHARE', 'Share')
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="interactions"
    )
    post = models.ForeignKey(
        "feed.Post",
        on_delete=models.CASCADE,
        related_name="interactions"
    )
    interaction_type = models.CharField(
        max_length=10,
        choices=INTERACTION_TYPES,
        default='VIEW'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post', 'interaction_type')
        ordering = ['-timestamp']
        verbose_name = "User Interaction"
        verbose_name_plural = "User Interactions"

    def __str__(self):
        return f"{self.user} {self.get_interaction_type_display()} {self.post}"

