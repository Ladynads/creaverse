from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, InviteCode, Message, UserInteraction, Profile

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'bio', 'get_profile_image', 'is_verified', 'is_active', 'is_staff')
    list_filter = ('is_verified', 'is_active', 'is_staff')

    fieldsets = UserAdmin.fieldsets + (
        ("Profile Info", {"fields": ("bio", "profile_image")}),
        ("Verification", {"fields": ("is_verified",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profile Info", {"fields": ("bio", "profile_image")}),
        ("Verification", {"fields": ("is_verified",)}),
    )

    def get_profile_image(self, obj):
        return obj.profile_image.url if obj.profile_image else "No image"
    get_profile_image.short_description = 'Profile Image'


# Invite Code Admin
class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "created_by", "used_by", "created_at", "used_at")
    search_fields = ("code", "created_by__username", "used_by__username")
    list_filter = ("created_at", "used_at")
    date_hierarchy = 'created_at'
    raw_id_fields = ('created_by', 'used_by')

# Comment Admin
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "content", "created_at")
    search_fields = ("content", "user__username", "post__content")
    list_filter = ("created_at",)
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'post')

# Message Admin
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "truncated_content", "created_at", "is_read")
    search_fields = ("content", "sender__username", "receiver__username")
    list_filter = ("is_read", "created_at")
    date_hierarchy = 'created_at'
    raw_id_fields = ('sender', 'receiver')
    
    def truncated_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    truncated_content.short_description = 'Content'

# User Interaction Admin
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "get_interaction_display", "timestamp")
    list_filter = ("interaction_type", "timestamp")
    search_fields = ("user__username", "post__content")
    date_hierarchy = 'timestamp'
    raw_id_fields = ('user', 'post')
    
    def get_interaction_display(self, obj):
        return obj.get_interaction_type_display()
    get_interaction_display.short_description = 'Interaction'

# Safe Registration
if not admin.site.is_registered(CustomUser):
    admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(InviteCode, InviteCodeAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(UserInteraction, UserInteractionAdmin)

# Profile Admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)
