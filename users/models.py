import random
import string
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

# Function to generate unique invite codes
def generate_invite_code():
    """Generates an 8-character alphanumeric invite code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def validate_bio_length(value):
    """Validator that checks bio doesn't exceed 500 chars"""
    if value and len(value) > 500:
        raise ValidationError("Bio cannot exceed 500 characters")

def upload_to_profile_pics(instance, filename):
    """Custom upload path for profile pictures"""
    return f'profile_pics/{instance.username}/{filename}'

class CustomUser(AbstractUser):
    """Extended user model with social features."""
    bio = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        help_text=_("Tell others about yourself (max 500 chars)"),
        validators=[validate_bio_length]
    )
    profile_image = models.ImageField(
        upload_to=upload_to_profile_pics,
        blank=True,
        null=True,
        help_text=_("Upload a profile picture"),
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])]
    )
    used_invite = models.BooleanField(
        default=False,
        help_text=_("Has this user used an invite code?")
    )
    social_links = JSONField(
        default=dict,
        blank=True,
        help_text=_("Social media links in JSON format")
    )
    is_verified = models.BooleanField(
        default=False,
        help_text=_("Designates whether the user is verified")
    )
    last_seen = models.DateTimeField(
        auto_now=True,
        help_text=_("Last time the user was active")
    )
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True,
        help_text=_("Users this user is following")
    )

    @property
    def is_online(self):
        """Check if user is currently online."""
        return self.last_seen > now() - timedelta(minutes=15)

    def get_profile_image(self):
        """Returns the profile image URL or default if none exists."""
        if self.profile_image and hasattr(self.profile_image, "url"):
            return self.profile_image.url
        return static("profile_pics/default_profile.webp")

    def get_social_link(self, platform):
        """Get specific social link if exists."""
        return self.social_links.get(platform, '')

    def clean(self):
        """Additional model validation."""
        super().clean()
        if self.bio and len(self.bio) > 500:
            raise ValidationError({'bio': "Bio cannot exceed 500 characters"})

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['last_seen']),
        ]

    def __str__(self):
        return self.username

class InviteCode(models.Model):
    """System for invite-only registrations."""
    code = models.CharField(
        max_length=10,
        unique=True,
        default=generate_invite_code,
        help_text=_("Unique invite code")
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="generated_invites",
        help_text=_("User who created this invite")
    )
    used_by = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invite_used",
        help_text=_("User who redeemed this invite")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def mark_used(self, user):
        """Records when an invite code is used."""
        if self.used_by:
            raise ValidationError(_("This invite code has already been used"))
        self.used_by = user
        self.used_at = now()
        self.save()

    def is_valid(self):
        """Check if the invite code is still usable."""
        return not bool(self.used_by)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Invite Code")
        verbose_name_plural = _("Invite Codes")
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        status = _("Used") if self.used_by else _("Active")
        return f"{self.code} ({status})"

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
        verbose_name = _("Private Message")
        verbose_name_plural = _("Private Messages")
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"Message {self.id}"

class UserInteraction(models.Model):
    """Tracks all user interactions across the platform."""
    INTERACTION_TYPES = [
        ('LIKE', _('Like')),
        ('COMMENT', _('Comment')),
        ('VIEW', _('View')),
        ('SHARE', _('Share')),
        ('FOLLOW', _('Follow')),
        ('BOOKMARK', _('Bookmark')),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="interactions"
    )
    post = models.ForeignKey(
        "feed.Post",
        on_delete=models.CASCADE,
        related_name="post_interactions",
        null=True,
        blank=True
    )
    target_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="targeted_interactions",
        null=True,
        blank=True
    )
    interaction_type = models.CharField(
        max_length=10,
        choices=INTERACTION_TYPES
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional interaction data")
    )

    class Meta:
        unique_together = [
            ('user', 'post', 'interaction_type'),
            ('user', 'target_user', 'interaction_type'),
        ]
        ordering = ['-timestamp']
        verbose_name = _("User Interaction")
        verbose_name_plural = _("User Interactions")
        indexes = [
            models.Index(fields=['user', 'interaction_type']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        target = self.post or self.target_user
        return f"{self.user} {self.get_interaction_type_display()} {target}"

    def clean(self):
        """Validate that either post or target_user is set."""
        if not self.post and not self.target_user:
            raise ValidationError(
                _("Interaction must be with a post or user")
            )
        if self.post and self.target_user:
            raise ValidationError(
                _("Interaction can't reference both post and user")
            )

