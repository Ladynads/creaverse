from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q, F, Value, IntegerField, Case, When
from django.utils.timezone import now
from django.views.decorators.http import require_POST
import datetime
from feed.models import Post, Like
from .models import Comment   

# AI-Powered Feed View
@login_required
def feed_view(request):
    """Fetches posts with AI-powered recommendations, trending posts, and latest posts."""

    # Fetch user interactions (posts they liked or commented on)
    user_interactions = Post.objects.filter(
        Q(likes__user=request.user) | Q(comments__user=request.user)  
    ).distinct()

    # Extract keywords from interacted posts
    interacted_keywords = set()
    for post in user_interactions:
        if hasattr(post, 'keywords') and post.keywords:  
            interacted_keywords.update(post.keywords.split(', '))

    # Convert set to list for filtering
    interacted_keywords = list(interacted_keywords)

    # Get posts matching those keywords (excluding the user's own posts)
    recommended_posts = Post.objects.filter(
        Q(keywords__in=interacted_keywords)
    ).exclude(user=request.user).distinct() if interacted_keywords else Post.objects.none()

    # Add ranking based on likes & comments
    trending_posts = Post.objects.annotate(
        num_likes=Count('likes'),
        num_comments=Count('comments'),
        relevance_score=F('num_likes') * 2 + F('num_comments')  # Weighted ranking
    ).order_by('-relevance_score', '-created_at')

    # Get latest posts but make sure they are not too old
    time_threshold = now() - datetime.timedelta(days=7)
    latest_posts = Post.objects.filter(created_at__gte=time_threshold).order_by('-created_at')

    # Personalization: Boost posts that user has interacted with
    personalized_posts = Post.objects.annotate(
        interacted=Case(
            When(likes__user=request.user, then=Value(1)),  # Fixed: Changed likes= to likes__user=
            When(comments__user=request.user, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by('-interacted', '-created_at')

    # Combine: Prioritize recommended -> personalized -> trending -> latest
    all_posts = list(recommended_posts) + list(personalized_posts) + list(trending_posts) + list(latest_posts)

    # Remove duplicate posts
    seen = set()
    unique_posts = []
    for post in all_posts:
        if post.id not in seen:
            seen.add(post.id)
            unique_posts.append(post)

    return render(request, 'feed/feed.html', {'posts': unique_posts})


# Create Post
@login_required
def create_post(request):
    """Allows users to create posts."""
    if request.method == "POST":
        content = request.POST.get("content")
        if content.strip():
            Post.objects.create(user=request.user, content=content)
    return redirect("feed")


# View Single Post
@login_required
def post_detail_view(request, post_id):
    """Displays the details of a single post along with comments."""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('created_at')
    return render(request, 'feed/post_detail.html', {'post': post, 'comments': comments})


# Like Post
@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'success': True,
        'liked': liked,
        'new_like_count': post.likes.count()
    })


# Add Comment
@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    content = request.POST.get("content")

    if content.strip():
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            content=content
        )
        return JsonResponse({
            'success': True,
            'comment_text': comment.content,
            'username': comment.user.username,
            'timestamp': comment.created_at.strftime('%b %d, %Y, %I:%M %p')
        })

    return JsonResponse({'success': False, 'error': 'Comment cannot be empty'})


# Delete Post
@login_required
@require_POST
def delete_post(request, post_id):
    """Allows the post owner to delete their post."""
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user:
        post.delete()
    return redirect('feed')


# Delete Comment
@login_required
@require_POST
def delete_comment(request, comment_id):
    """Allows the comment owner or post owner to delete a comment."""
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user or comment.post.user == request.user:
        comment.delete()
    return redirect('post_detail', post_id=comment.post.id)

