from django.urls import path
from .views import register, CustomLoginView, CustomLogoutView, profile, ProfileUpdateView  # Import profile views

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', profile, name='profile'),  # Profile page
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),  # Edit profile page
]
