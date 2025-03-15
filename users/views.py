from django.shortcuts import render, redirect  # Import render & redirect
from django.contrib.auth import login, logout  # Import login & logout functions
from .forms import CustomUserCreationForm  # Import custom user creation form
from django.contrib.auth.views import LoginView, LogoutView  # Import login/logout views
from django.urls import reverse_lazy  # Import reverse_lazy for redirects
from django.views import View  # Import generic View class
from django.contrib.auth.decorators import login_required  # Restrict access to profile view
from django.utils.decorators import method_decorator  # Restrict access to profile edit view
from django.views.generic import UpdateView, ListView, CreateView  
from django.contrib.auth import get_user_model
from .models import Post  # Import Post model

# User Registration View
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to homepage after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# Login View 
class CustomLoginView(LoginView):
    template_name = 'users/login.html'

# Logout View 
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')  # Redirect after logout

    def post(self, request, *args, **kwargs):
        """Logout user on POST request (More secure)"""
        logout(request)
        return redirect(self.next_page)

# Profile View (Only for logged-in users)
@login_required
def profile(request):
    return render(request, 'users/profile.html')  # Displays user profile page

# Profile Update View (Only for logged-in users)
@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = get_user_model()  # Uses the CustomUser model
    fields = ['username', 'email', 'bio', 'profile_image']  # Fields the user can edit
    template_name = 'users/profile_edit.html'  # Uses profile_edit.html template
    success_url = reverse_lazy('profile')  # Redirects to profile page after saving changes

    def get_object(self):
        return self.request.user  # Only allows editing of the logged-in user

# Feed View: Shows all posts
class FeedView(ListView):
    model = Post
    template_name = 'users/feed.html'
    context_object_name = 'posts'
    ordering = ['-created_at']  # Show newest posts first

# Create Post View: Allows users to create posts
@method_decorator(login_required, name='dispatch')
class CreatePostView(CreateView):
    model = Post
    fields = ['content']
    template_name = 'users/new_post.html'
    success_url = reverse_lazy('feed')  # Redirect to feed after posting

    def form_valid(self, form):
        form.instance.user = self.request.user  # Set post owner
        return super().form_valid(form)