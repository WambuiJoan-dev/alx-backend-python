# messaging_app/chats/permissions.py

from rest_framework.permissions import BasePermission
from .models import Conversation, Message

class IsParticipantOfConversation(BasePermission):
    """
    Custom permission to:
    1. Only allow authenticated users.
    2. Only allow participants of a conversation to access it or its messages.
    """

    def has_permission(self, request, view):
        """
        Check 1: Allow only authenticated users.
        This is technically redundant if IsAuthenticated is global,
        but it's good practice.
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check 2: Allow only participants to view/edit.
        This is called for detail views (GET, PUT, PATCH, DELETE on /conversations/1/)
        """
        
        # If the object is a Conversation
        if isinstance(obj, Conversation):
            # Check if the user is in the 'participants' list
            return obj.participants.filter(id=request.user.id).exists()

        # If the object is a Message
        if isinstance(obj, Message):
            # Check if the user is a participant in the message's conversation
            return obj.conversation.participants.filter(id=request.user.id).exists()

        return False