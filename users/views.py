from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q
from .forms import CustomUserCreationForm, MessageForm
from .models import CustomUser, InviteCode, Message
from feed.models import Post

# ✅ User model
from django.contrib.auth import get_user_model
User = get_user_model()

# ✅ Invite-Only User Registration View
def register(request):
    """Handles user registration with invite code verification."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        invite_code = request.POST.get("invite_code")

        if form.is_valid():
            try:
                invite = InviteCode.objects.get(code=invite_code, used_by__isnull=True)
            except InviteCode.DoesNotExist:
                return render(request, 'users/register.html', {'form': form, 'error': "Invalid or used invite code!"})

            user = form.save()
            invite.mark_used(user)
            login(request, user)
            return redirect('feed')

    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


# ✅ Home View (Shows Unread Messages Count)
def home_view(request):
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    
    return render(request, "home.html", {"unread_count": unread_count})


# ✅ Login View
class CustomLoginView(LoginView):
    template_name = 'users/login.html'


# ✅ Logout View
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.next_page)


# ✅ View Own Profile
@login_required
def profile_view(request):
    """Displays the logged-in user's profile & posts."""
    user_posts = Post.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users/profile.html', {
        'profile_user': request.user,
        'user_posts': user_posts,
    })


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
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'users/profile_edit.html')


# ✅ View Other User Profiles
@login_required
def user_profile(request, username):
    """Allows viewing another user's profile & their posts."""
    profile_user = get_object_or_404(CustomUser, username=username)
    user_posts = Post.objects.filter(user=profile_user).order_by('-created_at')

    return render(request, 'users/user_profile.html', {
        'profile_user': profile_user,
        'user_posts': user_posts,
    })


# ✅ Invite Friends System
@login_required
def invite_view(request):
    """Shows user's invite codes."""
    invite_codes = InviteCode.objects.filter(created_by=request.user)
    return render(request, "users/invite.html", {"invite_codes": invite_codes})

@login_required
@csrf_protect
def send_invite_email(request):
    """Handles sending an invite code via email."""
    if request.method == "POST":
        email = request.POST.get('email')
        code = request.POST.get('code')

        if email and code:
            try:
                send_mail(
                    "You're Invited to Join CreatorVerse!",
                    f"Hey! You've been invited to join CreatorVerse.\n\nUse this invite code: {code}\n\nSign up here: http://127.0.0.1:8000/register/",
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return JsonResponse({'success': True, 'message': 'Invite sent successfully!'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request!'})



# ✅ Generate Invite Code
@login_required
def generate_invite(request):
    if InviteCode.objects.filter(created_by=request.user).count() >= 5:
        return JsonResponse({"success": False, "error": "Invite limit reached!"})

    new_code = InviteCode.objects.create(created_by=request.user)
    return JsonResponse({"success": True, "code": new_code.code})


# ✅ Private Messaging System
@login_required
def message_list(request):
    """View to show received and sent messages."""
    received_messages = Message.objects.filter(receiver=request.user).select_related("sender").order_by('-created_at')
    sent_messages = Message.objects.filter(sender=request.user).select_related("receiver").order_by('-created_at')

    # Paginate received messages
    received_paginator = Paginator(received_messages, 10)  # Show 10 messages per page
    received_page = request.GET.get('received_page')
    received_messages = received_paginator.get_page(received_page)

    # Paginate sent messages
    sent_paginator = Paginator(sent_messages, 10)  # Show 10 messages per page
    sent_page = request.GET.get('sent_page')
    sent_messages = sent_paginator.get_page(sent_page)

    return render(request, "users/message_list.html", {
        "received_messages": received_messages,
        "sent_messages": sent_messages
    })


@login_required
def send_message(request, user_id):
    """Send a private message to another user."""
    receiver = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()

            messages.success(request, f"Message sent to {receiver.username} successfully!")
            return redirect("message_thread", receiver_id=receiver.id)

    else:
        form = MessageForm()

    return render(request, "users/send_message.html", {"form": form, "receiver": receiver})


@login_required
def message_thread(request, receiver_id):
    """Displays the conversation thread between two users."""
    receiver = get_object_or_404(CustomUser, id=receiver_id)

    # Retrieve full conversation between sender & receiver
    messages_thread = Message.objects.filter(
        Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)
    ).order_by("created_at")

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            messages.success(request, "Reply sent successfully!")
            return redirect("message_thread", receiver_id=receiver.id)

    else:
        form = MessageForm()

    return render(
        request,
        "users/message_thread.html",
        {"receiver": receiver, "messages": messages_thread, "form": form}
    )


# ✅ Delete Message
@login_required
def delete_message(request, message_id):
    """Allows sender or receiver to delete a message."""
    message = get_object_or_404(Message, id=message_id)

    if request.user == message.sender or request.user == message.receiver:
        message.delete()

    return redirect(request.META.get("HTTP_REFERER", "message_list"))  # Redirect to previous page

def feed_view(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'feed/feed.html', {'posts': posts})















