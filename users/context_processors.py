from users.models import Message


def site_settings(request):
    from django.conf import settings
    return {
        'SITE_NAME': 'CreatorVerse',
        'SITE_URL': settings.SITE_URL,
    }

def unread_messages(request):
    if request.user.is_authenticated:
        from users.models import Message
        return {
            'unread_count': Message.objects.filter(
                receiver=request.user,
                is_read=False
            ).count()
        }
    return {}