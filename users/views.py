from django.shortcuts import render, redirect, get_object_or_404  # Import necessary functions
from django.contrib.auth import login, logout  # Import login & logout
from django.contrib.auth.views import LoginView, LogoutView  # Import Django login/logout views
from django.urls import reverse_lazy  # Reverse lazy for redirects
from django.contrib.auth.decorators import login_required  # Restrict access to logged-in users
from django.utils.decorators import method_decorator  # Decorator for class-based views
from django.http import JsonResponse  # For handling likes asynchronously
from django.views.generic import UpdateView, ListView, CreateView  # Class-based views
from django.contrib.auth import get_user_model  # Get the user model
from .forms import CustomUserCreationForm  # Import user creation form
from .models import Post, Comment  # Import Post & Comment models

# User Registration View
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')  # Redirect to feed after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


# Login View
class CustomLoginView(LoginView):
    template_name = 'users/login.html'


# Logout View (POST request only for security)
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')  # Redirect after logout

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.next_page)


# User Profile View
@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})


# Profile Update View (Only for logged-in users)
@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = get_user_model()  # Uses the CustomUser model
    fields = ['username', 'email', 'bio', 'profile_image']  # Fields the user can edit
    template_name = 'users/profile_edit.html'  # Uses profile_edit.html template
    success_url = reverse_lazy('profile')  # Redirects to profile page after saving changes

    def get_object(self):
        return self.request.user  # Only allows editing of the logged-in user


# Feed View (List of posts)
class FeedView(ListView):
    model = Post
    template_name = 'feed/feed.html'
    context_object_name = 'posts'
    ordering = ['-created_at']  # Show newest posts first


# Create Post
@method_decorator(login_required, name='dispatch')
class CreatePostView(CreateView):
    model = Post
    fields = ['content']
    template_name = 'users/new_post.html'
    success_url = reverse_lazy('feed')  # Redirect to feed after posting

    def form_valid(self, form):
        form.instance.user = self.request.user  # Set post owner
        return super().form_valid(form)


# Like/Unlike a Post (AJAX Request)
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)  # Unlike if already liked
        liked = False
    else:
        post.likes.add(request.user)  # Like the post
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': post.total_likes()})


# Add Comment to Post
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            Comment.objects.create(user=request.user, post=post, content=content)
    return redirect('feed')


# Delete Post
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user:  # Only allow the owner to delete
        post.delete()
    return redirect('feed')


# Delete Comment
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user or comment.post.user == request.user:  # Owner or post creator can delete
        comment.delete()
    return redirect('feed')
