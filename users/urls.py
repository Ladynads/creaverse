from django.urls import path
from .views import (
    register, CustomLoginView, CustomLogoutView, profile_view, profile_edit, 
    feed_view, create_post, like_post, add_comment, delete_post, delete_comment,
    message_list, send_message, message_thread, user_profile
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

    # ✅ Feed & Posts Routes
    path('feed/', feed_view, name='feed'),
    path('feed/new/', create_post, name='new_post'),

    # ✅ Interactive Features (Like, Comment, Delete)
    path('post/<int:post_id>/like/', like_post, name='like_post'),
    path('post/<int:post_id>/comment/', add_comment, name='add_comment'),
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),

    # ✅ Private Messaging (DMs)
    path('messages/', message_list, name='message_list'),
    path('messages/send/<int:receiver_id>/', send_message, name='send_message'),
    path('messages/thread/<int:receiver_id>/', message_thread, name='message_thread'),
]





