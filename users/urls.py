from django.urls import path
from .views import (
    register, CustomLoginView, CustomLogoutView, profile_view, profile_edit, user_profile,
    message_list, send_message, message_thread, delete_message,  
    generate_invite, send_invite_email, invite_view
)

urlpatterns = [
    # ✅ Authentication Routes
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # ✅ Profile Routes
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    path('profile/<str:username>/', user_profile, name='user_profile'),

    # ✅ Private Messaging (DMs)
    path('messages/', message_list, name='message_list'),  # ✅ Message List
    path('messages/send/<int:user_id>/', send_message, name='send_message'),  # ✅ Send Message
    path('messages/thread/<int:receiver_id>/', message_thread, name='message_thread'),  # ✅ Message Thread
    path('messages/delete/<int:message_id>/', delete_message, name='delete_message'),  # ✅ Delete Message

    # ✅ Invite Code System
    path("invite/", invite_view, name="invite_friends"),  # ✅ Invite Page
    path("invite/generate/", generate_invite, name="generate_invite"),  # ✅ Generate Invite Code
    path("invite/send-email/", send_invite_email, name="send_invite_email"),  # ✅ Send Invite via Email
]











