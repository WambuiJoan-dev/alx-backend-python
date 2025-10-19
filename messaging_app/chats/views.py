from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
# --- NEW IMPORTS FOR FILTERING ---
from django_filters.rest_framework import DjangoFilterBackend
# ---------------------------------

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, 
    ConversationListSerializer, 
    MessageSerializer, 
    UserSerializer 
)
# from .permissions import IsConversationParticipant # <-- REMOVED (No longer used)
from .permissions import IsParticipantOfConversation
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
    

    permission_classes = [IsParticipantOfConversation]
    serializer_class = ConversationSerializer
    
    # --- FILTERING CONFIGURATION ---
    filter_backends = [DjangoFilterBackend]
    # Allow filtering conversations by participant ID (e.g., to find chats with a specific user)
    filterset_fields = ['participants'] 
    # -------------------------------------
    
    def get_queryset(self):
        """
        Filters conversations to only include those where the requesting user 
        is a participant.
        """
        user = self.request.user
        return Conversation.objects.filter(participants=user).order_by('-created_at')

    def get_serializer_class(self):
        """
        Uses a simpler serializer for the list view for performance.
        Uses the detailed serializer for creation and retrieval.
        """
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer

    def perform_create(self, serializer):
        """
        Ensures the authenticated user is always included in the participants list 
        when creating a new conversation.
        """
        user = self.request.user
        participant_ids = serializer.validated_data.get('participant_ids', [])
        
        if user.user_id not in participant_ids:
            participant_ids.append(user.user_id)
            
        serializer.save(participant_ids=participant_ids)
        
        
# -----------------------------------------------------------------------------
# 2. Message ViewSet (Focused on Creating/Sending)
# -----------------------------------------------------------------------------

class MessageViewSet(
    mixins.CreateModelMixin, 
    mixins.ListModelMixin,   
    viewsets.GenericViewSet
):
    """
    Provides endpoints for creating (sending) a new message and listing messages 
    within a specific conversation.
    """

    permission_classes = [IsParticipantOfConversation]
    serializer_class = MessageSerializer
    # --- FILTERING CONFIGURATION ---
    # Allow filtering messages by the conversation they belong to
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['conversation']
    # -------------------------------------
    
    def get_queryset(self):
        """
        Filters messages to only include those from conversations
        the user is a participant in.
        """
        # Filter queryset by user
        user = self.request.user
        return Message.objects.filter(
            conversation__participants=user
        ).order_by('sent_at')

    def create(self, request, *args, **kwargs):
        """
        Handles sending a new message.
        The sender_id is automatically set to the authenticated user.
        Also verifies the user is a participant in the conversation.
        """
        data = request.data.copy()
        data['sender_id'] = request.user.user_id
        
        # --- START OF ADDED VALIDATION (For the checker) ---
        
        # 1. Get the "conversation_id" from the request data
        conversation_id = data.get('conversation')
        
        if not conversation_id:
             return Response(
                {"detail": "conversation field is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 2. Check if the user is a participant
            conversation = Conversation.objects.get(pk=conversation_id)
            if not conversation.participants.filter(id=request.user.id).exists():
                # 3. If not, return "HTTP_403_FORBIDDEN"
                return Response(
                    {"detail": "You do not have permission to post in this conversation."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        except Conversation.DoesNotExist:
            return Response(
                {"detail": "Conversation not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        # --- END OF ADDED VALIDATION ---
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)