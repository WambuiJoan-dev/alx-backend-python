from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, 
    ConversationListSerializer, 
    MessageSerializer, 
    UserSerializer # Import UserSerializer if needed for specific responses
)


# -----------------------------------------------------------------------------
# 1. Conversation ViewSet
# -----------------------------------------------------------------------------

class ConversationViewSet(viewsets.ModelViewSet):
    """
    Provides endpoints for listing, retrieving, and creating conversations.
    - list: Get all conversations the current user is a part of.
    - retrieve: Get details of a specific conversation, including nested messages.
    - create: Start a new conversation (requires participant IDs).
    """
    
    # Enforce that only logged-in users can access these views
    permission_classes = [IsAuthenticated]
    
    # Default serializer for detailed views (includes nested messages)
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        """
        Filters conversations to only include those where the requesting user 
        is a participant.
        """
        # The requesting user is available via self.request.user
        user = self.request.user
        
        # Filter all conversations where 'participants' contains the current user
        return Conversation.objects.filter(participants=user).order_by('-created_at')

    def get_serializer_class(self):
        """
        Uses a simpler serializer for the list view for performance.
        Uses the detailed serializer for creation and retrieval.
        """
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer

    # Custom create implementation to automatically include the authenticated user
    def perform_create(self, serializer):
        """
        Ensures the authenticated user is always included in the participants list 
        when creating a new conversation.
        """
        user = self.request.user
        
        # Get the list of participant IDs provided in the request body
        # participant_ids is a write_only field defined in ConversationSerializer
        participant_ids = serializer.validated_data.get('participant_ids', [])
        
        # Ensure the current user's ID is in the list, removing duplicates
        if user.user_id not in participant_ids:
            participant_ids.append(user.user_id)
            
        # Manually save the conversation instance, passing the full set of IDs
        # The ConversationSerializer's create method will handle the M2M relationship
        serializer.save(participant_ids=participant_ids)
        
        # Response status is handled by ModelViewSet default behavior


# -----------------------------------------------------------------------------
# 2. Message ViewSet (Focused on Creating/Sending)
# -----------------------------------------------------------------------------

class MessageViewSet(
    mixins.CreateModelMixin, # Only allow POST (Create)
    mixins.ListModelMixin,   # Allow GET (List messages within a conversation)
    viewsets.GenericViewSet
):
    """
    Provides endpoints for creating (sending) a new message and listing messages 
    within a specific conversation.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        """
        Returns all messages, but this ViewSet is primarily used nested under 
        a conversation URL, making the list action less common here.
        If we were to implement a list, it would be filtered by conversation ID.
        """
        # We will usually rely on the nested URL structure for listing messages,
        # but for a simple ModelViewSet, we default to all messages for now.
        return Message.objects.all().order_by('sent_at')

    def create(self, request, *args, **kwargs):
        """
        Handles sending a new message.
        Requires 'message_body' and 'conversation_id' in the request body.
        The sender_id is automatically set to the authenticated user.
        """
        data = request.data.copy()
        
        # Set the sender_id automatically from the authenticated user
        data['sender_id'] = request.user.user_id
        
        # Pass the modified data to the serializer
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
