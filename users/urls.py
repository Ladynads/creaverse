from django.urls import path  # Import path for URL patterns
from .views import (  # Import all necessary views
    register, CustomLoginView, CustomLogoutView, profile_view, ProfileUpdateView, 
    FeedView, CreatePostView, like_post, add_comment, delete_post, delete_comment
)

urlpatterns = [
    # Authentication Routes
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # Profile Routes
    path('profile/', profile_view, name='profile'),  # View Profile
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),  # Edit Profile

    # Feed & Posts Routes
    path('feed/', FeedView.as_view(), name='feed'),  # Main Feed Page
    path('feed/new/', CreatePostView.as_view(), name='new_post'),  # Create Post

    # Interactive Features (Like, Comment, Delete)
    path('post/<int:post_id>/like/', like_post, name='like_post'),  # Like a post
    path('post/<int:post_id>/comment/', add_comment, name='add_comment'),  # Comment on a post
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),  # Delete a post
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),  # Delete a comment
]
