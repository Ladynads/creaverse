from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, InviteCode, Post, Comment, Message, UserInteraction

# ✅ Register Custom User Model
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'bio', 'profile_image') 
    fieldsets = UserAdmin.fieldsets + (
        ("Profile Info", {"fields": ("bio", "profile_image")}),  
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profile Info", {"fields": ("bio", "profile_image")}),  
    )


# ✅ Register Invite Code Model
class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "created_by", "used_by", "created_at", "used_at")
    search_fields = ("code", "created_by__username", "used_by__username")
    list_filter = ("created_at", "used_at")


# ✅ Register Post Model
class PostAdmin(admin.ModelAdmin):
    list_display = ("user", "content", "created_at")
    search_fields = ("content", "user__username")
    list_filter = ("created_at",)


# ✅ Register Comment Model
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "content", "created_at")
    search_fields = ("content", "user__username", "post__content")
    list_filter = ("created_at",)


# ✅ Register Message Model
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "content", "created_at", "is_read")
    search_fields = ("content", "sender__username", "receiver__username")
    list_filter = ("is_read", "created_at")


# ✅ Register User Interaction Model
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "liked", "commented", "viewed", "timestamp")
    list_filter = ("liked", "commented", "viewed", "timestamp")


# ✅ Add to Django Admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(InviteCode, InviteCodeAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(UserInteraction, UserInteractionAdmin)

