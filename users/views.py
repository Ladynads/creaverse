from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from django.contrib.auth import get_user_model
from django.db.models import Count, F, ExpressionWrapper, FloatField, DurationField
from django.utils.timezone import now
import datetime
from .forms import CustomUserCreationForm
from .models import CustomUser, Post, Comment, Message

User = get_user_model()

# ✅ User Registration View
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')  
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


# ✅ Login View
class CustomLoginView(LoginView):
    template_name = 'users/login.html'


# ✅ Logout View (POST request only for security)
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.next_page)


# ✅ View Own Profile
@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})


# ✅ Edit Profile
@login_required
def profile_edit(request):
    if request.method == "POST":
        user = request.user
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.bio = request.POST.get('bio', user.bio)
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        user.save()
        return redirect('profile')

    return render(request, 'users/profile_edit.html')


# ✅ View Other User Profiles
@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    posts = Post.objects.filter(user=profile_user).prefetch_related('comments')

    return render(request, 'users/user_profile.html', {
        'profile_user': profile_user,
        'posts': posts
    })


# ✅ Trending Feed View (Trending + Latest Posts)
@login_required
def feed_view(request):
    """
    Fetches and displays posts, prioritizing trending posts based on likes, comments, and recency.
    """
    time_threshold = now() - datetime.timedelta(days=7)  # Posts older than 7 days decay in ranking

    posts = Post.objects.annotate(
        num_likes=Count('likes'),
        num_comments=Count('comments'),
        age_factor=ExpressionWrapper(
            (F('created_at') - time_threshold) / datetime.timedelta(days=1),  # Converts duration to days
            output_field=FloatField()
        ),
        trending_score=F('num_likes') * 3 + F('num_comments') * 2 + F('age_factor')
    ).order_by('-trending_score', '-created_at')

    return render(request, 'feed/feed.html', {'posts': posts})



# ✅ Create Post
@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST.get("content")
        if content.strip():
            Post.objects.create(user=request.user, content=content)
    return redirect("feed")


# ✅ Like/Unlike a Post (AJAX)
@csrf_exempt  
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({'liked': liked, 'total_likes': post.total_likes()})


# ✅ Add Comment (AJAX Support)
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            comment = Comment.objects.create(user=request.user, post=post, content=content)
            return JsonResponse({
                'success': True,
                'username': request.user.username,
                'comment': comment.content,
                'created_at': comment.created_at.strftime("%B %d, %Y %H:%M"),
                'comment_id': comment.id
            })
    return JsonResponse({'success': False})


# ✅ Delete Post
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user == request.user:
        post.delete()

    return redirect('feed')


# ✅ Delete Comment
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.user == request.user or comment.post.user == request.user:
        comment.delete()

    return redirect('feed')


# ✅ View All Conversations (Latest Message Per User)
@login_required
def message_list(request):
    latest_messages = Message.objects.filter(
        receiver=request.user
    ).values('sender').annotate(latest_message=Max('created_at')).order_by('-latest_message')

    conversations = []
    for msg in latest_messages:
        latest_msg = Message.objects.filter(sender_id=msg['sender'], created_at=msg['latest_message']).first()
        conversations.append(latest_msg)

    return render(request, 'messages/inbox.html', {'messages': conversations})


# ✅ Send Message
@login_required
def send_message(request, receiver_id):
    receiver = get_object_or_404(get_user_model(), id=receiver_id)

    if request.method == "POST":
        content = request.POST.get('content')
        if content.strip():
            Message.objects.create(sender=request.user, receiver=receiver, content=content)
            return redirect('message_list')

    return render(request, 'messages/send_message.html', {'receiver': receiver})


# ✅ View Message Thread (Conversation)
@login_required
def message_thread(request, receiver_id):
    receiver = get_object_or_404(get_user_model(), id=receiver_id)
    
    messages = Message.objects.filter(
        sender=request.user, receiver=receiver
    ) | Message.objects.filter(
        sender=receiver, receiver=request.user
    )
    
    messages = messages.order_by('created_at')

    # ✅ Mark received messages as read
    unread_messages = messages.filter(receiver=request.user, is_read=False)
    unread_messages.update(is_read=True)

    return render(request, 'messages/message_thread.html', {'messages': messages, 'receiver': receiver})


