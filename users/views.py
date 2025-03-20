from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm
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
    return render(request, 'home.html')


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
    """Displays the user's inbox with messages."""
    messages = Message.objects.filter(receiver=request.user)
    return render(request, 'messages/inbox.html', {'messages': messages})

@login_required
def send_message(request):
    """Allows users to send messages to each other."""
    if request.method == "POST":
        recipient_username = request.POST.get("recipient")
        content = request.POST.get("content")
        recipient = get_object_or_404(CustomUser, username=recipient_username)
        Message.objects.create(sender=request.user, receiver=recipient, content=content)
    return redirect('message_list')

@login_required
def message_thread(request, receiver_id):
    """Displays a conversation between two users."""
    other_user = get_object_or_404(CustomUser, id=receiver_id)
    messages = Message.objects.filter(
        (Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user))
    ).order_by("created_at")
    return render(request, 'messages/thread.html', {'messages': messages, 'other_user': other_user})



















