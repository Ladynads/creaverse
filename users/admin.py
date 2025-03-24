from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, InviteCode, Comment, Message, UserInteraction

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
    # Displaying the interaction types
    list_display = ("user", "post", "interaction_type", "timestamp")

    # Filter by interaction type
    list_filter = ("interaction_type", "timestamp")

    # Custom method to show if the post is liked
    def liked(self, obj):
        return obj.interaction_type == 'LIKE'
    
    liked.boolean = True
    liked.short_description = 'Liked'

    # Custom method to show if the post is commented
    def commented(self, obj):
        return obj.interaction_type == 'COMMENT'
    
    commented.boolean = True
    commented.short_description = 'Commented'

    # Custom method to show if the post is viewed
    def viewed(self, obj):
        return obj.interaction_type == 'VIEW'
    
    viewed.boolean = True
    viewed.short_description = 'Viewed'


# ✅ Add to Django Admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(InviteCode, InviteCodeAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(UserInteraction, UserInteractionAdmin)

