from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

User = get_user_model()

class Post(models.Model):
    """Post model with enhanced engagement tracking"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name=_("Author")
    )
    content = models.TextField(
        verbose_name=_("Content"),
        help_text=_("Share your creative content")
    )
    image = models.ImageField(
        upload_to="post_images/",
        blank=True,
        null=True,
        verbose_name=_("Image")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last updated")
    )
    is_draft = models.BooleanField(
        default=False,
        verbose_name=_("Draft status")
    )
    keywords = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Keywords")
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"Post #{self.id} by {self.user.username}"

    @property
    def like_count(self):
        """Optimized like count using cached relation"""
        return self.likes.count()

    @property
    def comment_count(self):
        """Optimized comment count"""
        return self.comments.count()

    def recent_comments(self, limit=3):
        """Get recent comments with prefetch"""
        return self.comments.select_related('user').order_by('-created_at')[:limit]

class Like(models.Model):
    """Tracks user likes for posts with metadata"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="post_likes",
        verbose_name=_("User")
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name=_("Post")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Liked at")
    )
    # Additional metadata
    REACTION_CHOICES = [
        ('like', _('Like')),
        ('love', _('Love')),
        ('laugh', _('Laugh')),
        ('wow', _('Wow')),
    ]

    reaction = models.CharField(
        max_length=20,
        default='like',
        choices=REACTION_CHOICES
    )

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = _("Like")
        verbose_name_plural = _("Likes")
        indexes = [
            models.Index(fields=['user', 'post']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user} → {self.post}"
class Comment(models.Model):
    """Enhanced comment model with threading"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="post_comments",
        verbose_name=_("Author")
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("Post")
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name=_("Parent comment")
    )
    content = models.TextField(
        verbose_name=_("Comment text")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last updated")
    )
    is_edited = models.BooleanField(
        default=False,
        verbose_name=_("Edited status")
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f"Comment by {self.user.username}"

    def save(self, *args, **kwargs):
        """Mark as edited when updating existing comment"""
        if self.pk:
            self.is_edited = True
        super().save(*args, **kwargs)


    
 