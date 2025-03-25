# Core Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.db.models import Q, Count, F, Prefetch
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db import transaction

# Forms & Models
from .forms import CustomUserCreationForm, MessageForm, ProfileEditForm
from .models import CustomUser as User, InviteCode, Message, UserInteraction
from feed.models import Post, Like, Comment

# Utilities
import logging
from datetime import timedelta
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# ===== Helper Functions =====
def get_unread_count(user):
    """Count unread messages for a user"""
    if not user.is_authenticated:
        return 0
    return Message.objects.filter(receiver=user, is_read=False).count()

# ===== HTMX Views =====
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


# ===== Authentication Views =====
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


# ===== Profile Views =====
@login_required
def profile_view(request, username):
    """View user profile with optimized queries and follow functionality"""
    profile_user = get_object_or_404(
        User.objects.prefetch_related('following', 'followers'),
        username=username
    )
    
    base_posts = Post.objects.filter(user=profile_user).select_related('user')
    
    context = {
        'profile_user': profile_user,
        'user_posts': base_posts.order_by('-created_at')[:20],
        'interactions': UserInteraction.objects.filter(
            user=profile_user
        ).select_related('post', 'target_user')[:5],
        'followers_count': profile_user.followers.count(),
        'following_count': profile_user.following.count(),
        'is_following': request.user.following.filter(id=profile_user.id).exists(),
        'is_online': profile_user.last_seen > timezone.now() - timezone.timedelta(minutes=15),
        'engagement_score': min(100, (
            (base_posts.count() * 2) + 
            (Like.objects.filter(post__user=profile_user).count() * 3) +
            (profile_user.followers.count() * 5)
        ) // 2),
        'has_cover_image': hasattr(profile_user, 'profile') and profile_user.profile.cover_image,
    }
    return render(request, 'users/profile.html', context)

@login_required
def profile_edit(request):
    """Edit profile with form handling including cover photo"""
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            
            # Handle cover photo separately if included in form
            if 'cover_image' in request.FILES:
                profile = user.profile
                profile.cover_image = request.FILES['cover_image']
                profile.save()
                
            messages.success(request, "Profile updated successfully!")
            return redirect('profile', username=user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'users/profile_edit.html', {
        'form': form,
        'social_links': getattr(request.user, 'social_links', {}),
        'has_cover_image': hasattr(request.user, 'profile') and request.user.profile.cover_image,
    })

@require_POST
@login_required
def update_cover(request):
    """Handle AJAX cover photo uploads with validation"""
    if not request.FILES.get('cover_image'):
        return JsonResponse({'success': False, 'error': 'No image provided'}, status=400)
    
    try:
        # Validate file size (max 5MB)
        if request.FILES['cover_image'].size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'Image size must be less than 5MB'
            }, status=400)
            
        # Validate file type
        valid_types = ['image/jpeg', 'image/png', 'image/webp']
        if request.FILES['cover_image'].content_type not in valid_types:
            return JsonResponse({
                'success': False,
                'error': 'Only JPEG, PNG, or WebP images are allowed'
            }, status=400)
        
        # Ensure profile exists
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        # Save the cover image
        profile.cover_image = request.FILES['cover_image']
        profile.save()
        
        return JsonResponse({
            'success': True,
            'new_cover_url': profile.cover_image.url,
            'message': 'Cover photo updated successfully!'
        })
        
    except Exception as e:
        logger.error(f"Cover upload error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Server error during upload'
        }, status=500)

# ===== Profile Tab Views =====
@login_required
def profile_tab_content(request, username, tab_name):
    """HTMX endpoint for tabbed content with optimized queries"""
    profile_user = get_object_or_404(
        User.objects.prefetch_related('following', 'followers'),
        username=username
    )
    
    # Base queryset with common select_related
    posts = Post.objects.select_related('user').filter(user=profile_user)
    
    if tab_name == 'likes':
        posts = Post.objects.filter(
            likes__user=profile_user
        ).distinct().select_related('user')
        template = 'users/partials/likes_tab.html'
    elif tab_name == 'saved' and profile_user == request.user:
        posts = Post.objects.filter(
            saved_by=profile_user
        ).select_related('user')
        template = 'users/partials/saved_tab.html'
    elif tab_name == 'drafts' and profile_user == request.user:
        posts = Post.objects.filter(
            user=profile_user,
            is_draft=True
        ).select_related('user')
        template = 'users/partials/drafts_tab.html'
    else:  # Default posts tab
        template = 'users/partials/posts_tab.html'
    
    return render(request, template, {
        'profile_user': profile_user,
        'posts': posts.order_by('-created_at')[:20],  # Consistent pagination
        'is_owner': profile_user == request.user,
    })

# ===== Social Interaction Views =====
@login_required
@require_POST
def follow_toggle(request, username):
    """Handle follow/unfollow actions via single endpoint"""
    target_user = get_object_or_404(User, username=username)
    
    if request.user == target_user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    
    # Toggle follow state
    if request.user.following.filter(id=target_user.id).exists():
        request.user.following.remove(target_user)
        action = 'unfollowed'
        # Remove interaction record
        UserInteraction.objects.filter(
            user=request.user,
            target_user=target_user,
            interaction_type='FOLLOW'
        ).delete()
    else:
        request.user.following.add(target_user)
        action = 'followed'
        # Create interaction record
        UserInteraction.objects.create(
            user=request.user,
            target_user=target_user,
            interaction_type='FOLLOW'
        )
    
    return JsonResponse({
        'action': action,
        'is_following': action == 'followed',
        'follower_count': target_user.followers.count(),
        'following_count': request.user.following.count()
    })

@login_required
def update_social_links(request):
    """Update social links via AJAX"""
    if request.method == "POST":
        request.user.social_links = {
            'twitter': request.POST.get('twitter', '').strip(),
            'instagram': request.POST.get('instagram', '').strip(),
            'website': request.POST.get('website', '').strip()
        }
        request.user.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

# ===== Invite System Views =====
@login_required
def invite_view(request):
    """View for managing invite codes"""
    invite_codes = InviteCode.objects.filter(
        created_by=request.user
    ).select_related('used_by')
    return render(request, "users/invite.html", {
        "invite_codes": invite_codes
    })

@login_required
@csrf_protect
def send_invite_email(request):
    """Send invite via email"""
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
    """Generate new invite code"""
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

# ===== Messaging Views =====
@login_required
def message_list(request):
    """List all messages"""
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
@require_http_methods(["GET", "POST"])
def send_message(request, user_id):
    recipient = get_object_or_404(User, id=user_id)
    
    # Clear any existing messages first
    message_storage = messages.get_messages(request)
    for message in message_storage:
        pass  # Consume all messages
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                message = form.save(commit=False)
                message.sender = request.user
                message.receiver = recipient
                message.save()
                
                # Create interaction record
                UserInteraction.objects.create(
                    from_user=request.user,
                    to_user=recipient,
                    interaction_type='message'
                )
                
                # Add ONE consistent success message
                messages.success(request, "Message sent successfully")
                return redirect('message_thread', receiver_id=user_id)
        
        # Form is invalid
        messages.error(request, "Please correct the errors below")
    else:
        form = MessageForm()
    
    return render(request, 'messaging/send_message.html', {
        'form': form,
        'recipient': recipient,
        'active_tab': 'messages'
    })

@login_required
def message_thread(request, receiver_id):
    """View message conversation thread"""
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
    """Delete a message"""
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'),
        id=message_id
    )

    if request.user in [message.sender, message.receiver]:
        message.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': "Permission denied"})

@login_required
def inbox_view(request):
    """Display the user's message inbox"""
    messages = Message.objects.filter(
        receiver=request.user
    ).order_by('-created_at')
    unread_count = messages.filter(is_read=False).count()
    
    context = {
        'messages': messages,
        'unread_count': unread_count
    }
    return render(request, 'messages/inbox.html', context)

# ===== Admin Views =====
@login_required
@staff_member_required
def verify_user(request, user_id):
    """Admin view to verify users"""
    user = get_object_or_404(User, id=user_id)
    user.is_verified = True
    user.save()
    return JsonResponse({'success': True, 'is_verified': True})

# ===== Home View =====
def home_view(request):
    """Home page view with featured creators"""
    featured_creators = (
        User.objects.filter(is_verified=True)
        .annotate(
            follower_count=Count('followers', distinct=True),
            post_count=Count('posts', distinct=True)
        )
        .only('username', 'bio', 'profile_image', 'is_verified')  # Optimize query
        .order_by('-follower_count', '-post_count')[:5]
    )

    unread_count = get_unread_count(request.user) if request.user.is_authenticated else 0

    return render(request, "home.html", {
        "featured_creators": featured_creators,
        "unread_count": unread_count,
        "now": timezone.now()
    })

# ===== Essential Views =====
def about_view(request):
    """About page view"""
    return render(request, 'about.html')

def privacy_policy(request): 
    """Privacy policy page"""
    return render(request, 'privacy.html')










