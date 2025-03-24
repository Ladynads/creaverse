from django.contrib import admin
from .models import Post, Comment
from django.utils.html import format_html

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'linked_post', 'truncated_content', 'created_at', 'is_edited', 'parent_info')
    list_filter = ('created_at', 'is_edited', 'post__user')
    search_fields = ('content', 'user__username', 'post__id')
    raw_id_fields = ('user', 'post', 'parent')
    list_select_related = ('user', 'post', 'parent')
    date_hierarchy = 'created_at'
    
    def truncated_content(self, obj):
        return (obj.content[:50] + '...') if len(obj.content) > 50 else obj.content
    truncated_content.short_description = 'Content'
    
    def parent_info(self, obj):
        return obj.parent.id if obj.parent else "—"
    parent_info.short_description = 'Parent ID'
    
    def linked_post(self, obj):
        url = f"/admin/feed/post/{obj.post.id}/change/"
        return format_html('<a href="{}">Post #{}</a>', url, obj.post.id)
    linked_post.short_description = 'Post'
    linked_post.admin_order_field = 'post__id'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'truncated_content', 'created_at', 'like_count', 'comment_count')
    list_filter = ('created_at', 'is_draft')
    search_fields = ('content', 'user__username', 'keywords')
    raw_id_fields = ('user',)
    readonly_fields = ('like_count', 'comment_count')
    
    def truncated_content(self, obj):
        return (obj.content[:75] + '...') if len(obj.content) > 75 else obj.content
    truncated_content.short_description = 'Content'
    
    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = 'Likes'
    
    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'