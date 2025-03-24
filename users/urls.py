from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Profiles
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # HTMX Profile Endpoints
    path('profile/<str:username>/stats/', views.user_stats_view, name='user_stats'),
    path('profile/<str:username>/<str:tab_name>/', views.profile_tab_content, name='profile_tab'),
    
    # Following
    path('profile/<str:username>/follow/', views.follow_toggle, name='follow_toggle'),
    
    # Messaging
    path('messages/', views.message_list, name='message_list'),
    path('messages/send/<int:user_id>/', views.send_message, name='send_message'),
    path('messages/thread/<int:receiver_id>/', views.message_thread, name='message_thread'),
    path('messages/delete/<int:message_id>/', views.delete_message, name='delete_message'),
    
    # Invites
    path('invite/', views.invite_view, name='invite_friends'),
    path('invite/generate/', views.generate_invite, name='generate_invite'),
    path('invite/send-email/', views.send_invite_email, name='send_invite_email'),
]













