from django.db import models
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from django.utils.text import slugify

nltk.download('stopwords')
nltk.download('punkt')

# ✅ Custom User Model
class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)  
    profile_image = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    invite_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.username
    
    # ✅ Function to return profile image or default static image
    def get_profile_image(self):
        """Returns the user's profile image or the default avatar if none is set."""
        if self.profile_image and hasattr(self.profile_image, "url"):
            return self.profile_image.url  # Use uploaded image
        return static("profile_pics/default_profile.webp")  # Serve default avatar


# ✅ Post Model (Interactive Feed with AI-powered Keywords)
class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)  
    likes = models.ManyToManyField(CustomUser, related_name='liked_posts', blank=True)  

    # ✅ AI Keyword Extraction
    keywords = models.TextField(blank=True, null=True)  # Stores extracted keywords

    class Meta:
        ordering = ['-created_at']

    def total_likes(self):
        return self.likes.count()

    def extract_keywords(self):
        """Extracts and stores keywords from post content using NLP."""
        stop_words = set(stopwords.words("english"))
        words = word_tokenize(self.content.lower())  # Tokenize text
        filtered_words = [w for w in words if w.isalnum() and w not in stop_words]  # Remove stop words
        return ", ".join(filtered_words[:10])  # Store top 10 keywords

    def save(self, *args, **kwargs):
        """Extract and store keywords before saving the post."""
        self.keywords = self.extract_keywords()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"


# ✅ Comment Model (For Posts)
class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')  
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')  
    content = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)  

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"


# ✅ Private Message Model (DMs)
class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# ✅ User Interaction Model (Tracks User Engagement)
class UserInteraction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='interactions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='interactions')
    liked = models.BooleanField(default=False)
    commented = models.BooleanField(default=False)
    viewed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.post.id} ({'Liked' if self.liked else ''} {'Commented' if self.commented else ''})"
