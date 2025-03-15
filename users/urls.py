from django.urls import path
from .views import (
    register, CustomLoginView, CustomLogoutView, profile_view, ProfileUpdateView, 
    feed_view, create_post, like_post, add_comment, delete_post, delete_comment,
    message_list, send_message, message_detail
)

urlpatterns = [
    # ✅ Authentication Routes
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # ✅ Profile Routes
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),

    # ✅ Feed & Posts Routes
    path('feed/', feed_view, name='feed'),
    path('feed/new/', create_post, name='new_post'),

    # ✅ Interactive Features (Like, Comment, Delete)
    path('post/<int:post_id>/like/', like_post, name='like_post'),
    path('post/<int:post_id>/comment/', add_comment, name='add_comment'),
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),

    # ✅ Private Messaging (DMs)
    path('messages/', message_list, name='message_list'),  # View all conversations
    path('messages/send/<int:receiver_id>/', send_message, name='send_message'),  # Send a new message
    path('messages/conversation/<int:receiver_id>/', message_detail, name='message_detail'),  # View conversation with a specific user
]



