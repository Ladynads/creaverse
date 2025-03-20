from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, F, ExpressionWrapper, FloatField, Q
from django.utils.timezone import now
import datetime
from users.models import Post, Comment 

# ✅ AI-Powered Feed View
@login_required
def feed_view(request):
    """Fetches posts using AI-powered recommendations and trending posts."""
    time_threshold = now() - datetime.timedelta(days=7)

    user_interactions = Post.objects.filter(
        Q(likes=request.user) | Q(comments__user=request.user)
    ).distinct()

    interacted_keywords = set()
    for post in user_interactions:
        if post.keywords:
            interacted_keywords.update(post.keywords.split(', '))

    recommended_posts = Post.objects.filter(
        Q(keywords__in=interacted_keywords)
    ).exclude(user=request.user).distinct()

    trending_posts = Post.objects.annotate(
        num_likes=Count('likes'),
        num_comments=Count('comments'),
    ).order_by('-num_likes', '-num_comments', '-created_at')

    latest_posts = Post.objects.order_by('-created_at')

    all_posts = list(recommended_posts) + list(trending_posts) + list(latest_posts)

    seen = set()
    unique_posts = []
    for post in all_posts:
        if post.id not in seen:
            seen.add(post.id)
            unique_posts.append(post)

    return render(request, 'feed/feed.html', {'posts': unique_posts})


# ✅ Create Post
@login_required
def create_post(request):
    """Allows users to create posts."""
    if request.method == "POST":
        content = request.POST.get("content")
        if content.strip():
            Post.objects.create(user=request.user, content=content)
    return redirect("feed")


# ✅ View Single Post
@login_required
def post_detail_view(request, post_id):
    """Displays the details of a single post along with comments."""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    return render(request, 'feed/post_detail.html', {'post': post, 'comments': comments})


# ✅ Like Post
@login_required
def like_post(request, post_id):
    """Allows users to like or unlike a post."""
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('feed')


# ✅ Add Comment
@login_required
def add_comment(request, post_id):
    """Allows users to add comments to a post."""
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        content = request.POST.get("content")
        if content.strip():
            Comment.objects.create(post=post, user=request.user, content=content)
    return redirect('post_detail', post_id=post.id)


# ✅ Delete Post
@login_required
def delete_post(request, post_id):
    """Allows the post owner to delete their post."""
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user:
        post.delete()
    return redirect('feed')


# ✅ Delete Comment
@login_required
def delete_comment(request, comment_id):
    """Allows the comment owner or post owner to delete a comment."""
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user or comment.post.user == request.user:
        comment.delete()
    return redirect('post_detail', post_id=comment.post.id)
