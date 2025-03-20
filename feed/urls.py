from django.urls import path
from .views import (
    feed_view, post_detail_view, create_post, delete_post, like_post, add_comment, delete_comment,
)

urlpatterns = [
    # ✅ Feed & Posts Routes
    path('', feed_view, name='feed'),
    path('post/new/', create_post, name='new_post'),
    path('post/<int:post_id>/', post_detail_view, name='post_detail'),
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),

    # ✅ Interactive Features (Like & Comment)
    path('post/<int:post_id>/like/', like_post, name='like_post'),
    path('post/<int:post_id>/comment/', add_comment, name='add_comment'),
    path('<int:post_id>/delete/', delete_post, name='delete_post'),
    path('comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),

   
]
