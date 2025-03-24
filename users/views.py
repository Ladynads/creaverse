# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q, Count
from django.utils import timezone
from .forms import CustomUserCreationForm, MessageForm, ProfileEditForm
from .models import CustomUser, InviteCode, Message, UserInteraction
from feed.models import Post, Like, Comment

User = get_user_model()  


# HTMX Views

@login_required
@require_http_methods(["GET"])
def user_stats_view(request, username):
    """HTMX endpoint for live user stats"""
    user = get_object_or_404(User, username=username)
    return JsonResponse({
        'post_count': Post.objects.filter(user=user).count(),
        'follower_count': user.followers.count(),
        'following_count': user.following.count()
    })

@login_required
def profile_tab_content(request, username, tab_name):
    """HTMX endpoint for tabbed content"""
    profile_user = get_object_or_404(User, username=username)
    
    if tab_name == 'likes':
        posts = Post.objects.filter(likes__user=profile_user).distinct()
        template = 'users/partials/likes_tab.html'
    elif tab_name == 'saved' and profile_user == request.user:
        posts = Post.objects.filter(saved_by=profile_user)
        template = 'users/partials/saved_tab.html'
    elif tab_name == 'drafts' and profile_user == request.user:
        posts = Post.objects.filter(user=profile_user, is_draft=True)
        template = 'users/partials/drafts_tab.html'
    else:
        posts = Post.objects.filter(user=profile_user)
        template = 'users/partials/posts_tab.html'

    return render(request, template, {
        'profile_user': profile_user,
        'posts': posts.order_by('-created_at')
    })


# Authentication Views

def register(request):
    """Invite-only registration with optimized queries"""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        invite_code = request.POST.get("invite_code")

        if form.is_valid():
            invite = get_object_or_404(
                InviteCode.objects.select_related('created_by'),
                code=invite_code, 
                used_by__isnull=True
            )
            user = form.save()
            invite.mark_used(user)
            login(request, user)
            return JsonResponse({'success': True})

    return render(request, 'users/register.html', {'form': form or CustomUserCreationForm()})

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect(self.next_page)


# Profile Views

@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(
        User.objects.select_related('profile'),
        username=username
    )
    
    base_posts = Post.objects.filter(user=profile_user)
    
    context = {
        'profile_user': profile_user,
        'user_posts': base_posts.order_by('-created_at'),
        'interactions': UserInteraction.objects.filter(
            user=profile_user
        ).select_related('post')[:5],
        'followers_count': profile_user.followers.count(),
        'following_count': profile_user.following.count(),
        'is_following': request.user.following.filter(id=profile_user.id).exists(),
        'is_online': profile_user.last_seen > timezone.now() - timezone.timedelta(minutes=15),
        'engagement_score': min(100, (
            (base_posts.count() * 2) + 
            (Like.objects.filter(post__user=profile_user).count() * 3) +
            (profile_user.followers.count() * 5)
        ) // 2),
    }
    return render(request, 'users/profile.html', context)

@login_required
def profile_edit(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile', username=user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'users/profile_edit.html', {
        'form': form,
        'social_links': getattr(request.user, 'social_links', {})
    })


# Social Interaction Views

@login_required
@require_http_methods(["POST"])
def follow_user(request, username):
    if request.user.username == username:
        return JsonResponse({'success': False, 'error': "Cannot follow yourself!"})
        
    user_to_follow = get_object_or_404(User, username=username)
    request.user.following.add(user_to_follow)
    
    UserInteraction.objects.create(
        user=request.user,
        target_user=user_to_follow,
        interaction_type='FOLLOW'
    )
    
    return JsonResponse({
        'success': True,
        'is_following': True,
        'follower_count': user_to_follow.followers.count()
    })

@login_required
@require_http_methods(["POST"])
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    request.user.following.remove(user_to_unfollow)
    return JsonResponse({
        'success': True,
        'is_following': False,
        'follower_count': user_to_unfollow.followers.count()
    })

@login_required
def update_social_links(request):
    if request.method == "POST":
        request.user.social_links = {
            'twitter': request.POST.get('twitter', '').strip(),
            'instagram': request.POST.get('instagram', '').strip(),
            'website': request.POST.get('website', '').strip()
        }
        request.user.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


# Invite System Views

@login_required
def invite_view(request):
    invite_codes = InviteCode.objects.filter(
        created_by=request.user
    ).select_related('used_by')
    return render(request, "users/invite.html", {
        "invite_codes": invite_codes
    })

@login_required
@csrf_protect
def send_invite_email(request):
    if request.method == "POST":
        email = request.POST.get('email')
        code = request.POST.get('code')

        if email and code:
            try:
                send_mail(
                    "You're Invited!",
                    f"Use code: {code}\nSign up: {settings.SITE_URL}/register/",
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def generate_invite(request):
    if InviteCode.objects.filter(created_by=request.user).count() >= 5:
        return JsonResponse({
            "success": False, 
            "error": "Maximum 5 invites!"
        })

    new_code = InviteCode.objects.create(created_by=request.user)
    return JsonResponse({
        "success": True, 
        "code": new_code.code
    })


# Messaging Views

@login_required
def message_list(request):
    messages = Message.objects.filter(
        Q(receiver=request.user) | Q(sender=request.user)
    ).select_related('sender', 'receiver').order_by('-created_at')
    
    paginator = Paginator(messages, 10)
    page = request.GET.get('page')
    messages = paginator.get_page(page)
    
    return render(request, "users/message_list.html", {
        "messages": messages
    })

@login_required
def send_message(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            return JsonResponse({'success': True})
    else:
        form = MessageForm()

    return render(request, "users/send_message.html", {
        "form": form,
        "receiver": receiver
    })

@login_required
def message_thread(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=receiver) |
        Q(sender=receiver, receiver=request.user)
    ).order_by("created_at")

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            return JsonResponse({'success': True})
    else:
        form = MessageForm()

    return render(request, "users/message_thread.html", {
        "receiver": receiver,
        "messages": messages,
        "form": form
    })

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'),
        id=message_id
    )

    if request.user in [message.sender, message.receiver]:
        message.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': "Permission denied"})


# Admin Views

@login_required
@staff_member_required
def verify_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_verified = True
    user.save()
    return JsonResponse({'success': True, 'is_verified': True})

# Home View

def home_view(request):
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(
            receiver=request.user, 
            is_read=False
        ).count()
    
    return render(request, "home.html", {
        "unread_count": unread_count
    })














