from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
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
            # ✅ Validate invite code
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

# ✅ Home View
def home_view(request):
    unread_count = 0  # Default unread count
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    
    return render(request, "home.html", {"unread_count": unread_count})


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
    """Displays the logged-in user's profile & posts."""
    user_posts = Post.objects.filter(user=request.user).order_by('-created_at')  # ✅ Fetch user's posts
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
        return redirect('profile')

    return render(request, 'users/profile_edit.html')


# ✅ View Other User Profiles
@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    return render(request, 'users/user_profile.html', {
        'profile_user': profile_user,
    })

@login_required
def invite_view(request):
    """Render the invite page with user's invite codes."""
    print("🔍 DEBUG: invite_view() was called")  # ✅ This will show in the terminal
    invite_codes = InviteCode.objects.filter(created_by=request.user)
    return render(request, "users/invite.html", {"invite_codes": invite_codes})


# ✅ Send Invite Email
@login_required
@csrf_exempt
def send_invite_email(request):
    """Handles sending an invite code via email."""
    if request.method == "POST":
        data = request.POST if request.POST else request.body.decode('utf-8')
        email = data.get('email')
        code = data.get('code')

        if email and code:
            try:
                send_mail(
                    "You're Invited to Join CreatorVerse!",
                    f"Hey there! 🎟 You've been invited to join CreatorVerse.\n\nUse this invite code to register: {code}\n\nSign up here: http://127.0.0.1:8000/register/",
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return JsonResponse({'success': True, 'message': 'Invite sent successfully!'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request!'})


# ✅ Generate Invite Code (For Users)
@login_required
def generate_invite(request):
    """Allows users to generate a limited number of invite codes."""
    if InviteCode.objects.filter(created_by=request.user).count() >= 5:
        return JsonResponse({"success": False, "error": "You have reached your invite limit!"})

    new_code = InviteCode.objects.create(created_by=request.user)
    return JsonResponse({"success": True, "code": new_code.code})


# ✅ Private Messaging Views
@login_required
def message_list(request):
    messages_received = Message.objects.filter(receiver=request.user).order_by("-created_at")
    messages_sent = Message.objects.filter(sender=request.user).order_by("-created_at")  # ✅ Show sent messages

    return render(
        request,
        "users/message_list.html",
        {"messages_received": messages_received, "messages_sent": messages_sent},
    )


@login_required
def send_message(request, user_id):
    receiver = get_object_or_404(CustomUser, id=user_id) 

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = receiver
            message.save()
            
            # ✅ Show success message
            messages.success(request, f"Message sent to {receiver.username} successfully!")
            
            # ✅ Redirect back to message list
            return redirect("message_list") 
    else:
        form = MessageForm()

    return render(request, "users/send_message.html", {"form": form, "receiver": receiver})

@login_required
def message_thread(request, receiver_id):
    receiver = get_object_or_404(CustomUser, id=receiver_id)
    messages_between = Message.objects.filter(
        sender=request.user, receiver=receiver
    ) | Message.objects.filter(sender=receiver, receiver=request.user)

    messages_between = messages_between.order_by("created_at")  # ✅ Oldest first

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
        {"messages_between": messages_between, "receiver": receiver, "form": form},
    )


@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    # Only allow sender or receiver to delete
    if request.user == message.sender or request.user == message.receiver:
        message.delete()
    
    return redirect("message_list")  # Redirect back to messages

@login_required
def message_list(request):
    """View to show received and sent messages"""
    received_messages = Message.objects.filter(receiver=request.user).order_by('-created_at') 
    sent_messages = Message.objects.filter(sender=request.user).order_by('-created_at')  

    return render(request, "users/message_list.html", {
        "received_messages": received_messages,
        "sent_messages": sent_messages
    })
















