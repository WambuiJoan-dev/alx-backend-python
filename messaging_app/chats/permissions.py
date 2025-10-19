# messaging_app/chats/permissions.py

from rest_framework.permissions import BasePermission
from rest_framework import permissions
from .models import Conversation, Message

class IsConversationParticipant(BasePermission):
    """
    Custom permission to only allow participants of a conversation
    to access its details and messages.
    """

    def has_object_permission(self, request, view, obj):
        # The user must be authenticated to even check object permissions
        if not request.user.is_authenticated:
            return False

        # If the object is a Conversation
        if isinstance(obj, Conversation):
            # Check if the user is in the 'participants' list
            return obj.participants.filter(id=request.user.id).exists()

        # If the object is a Message
        if isinstance(obj, Message):
            # Check if the user is a participant in the message's conversation
            return obj.conversation.participants.filter(id=request.user.id).exists()

        return False