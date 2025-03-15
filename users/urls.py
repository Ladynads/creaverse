from django.urls import path
from .views import register, CustomLoginView, CustomLogoutView, profile, ProfileUpdateView, FeedView, CreatePostView  # ✅ NEW: Import feed views

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('feed/', FeedView.as_view(), name='feed'),  # Feed page
    path('feed/new/', CreatePostView.as_view(), name='new_post'),  # Create post page
]
