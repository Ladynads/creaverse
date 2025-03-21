from users.models import Message

def unread_messages(request):
    """ ✅ Context Processor: Pass unread messages count to all templates """
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    else:
        unread_count = 0  # Default for logged-out users

    return {'unread_count': unread_count}
